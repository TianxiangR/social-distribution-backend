from api.models import FriendRequest, Follow
from api.serializer import AuthorRemoteSerializer, FriendRequestSerializer, FriendRequestListSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import get_or_create_user
from datetime import datetime
from ..api_lookup import API_LOOKUP
from urllib3.util import parse_url
from .inbox import handleInbox
from datetime import datetime


class FriendRequestList(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [TokenAuthentication]
  queryset = FriendRequest.objects.all()
  serializer_class = FriendRequestListSerializer
  
  
  def get(self, request, **kwargs):
    author = request.user
    friend_requests = FriendRequest.objects.filter(target=author)
    serializer = self.get_serializer(friend_requests, context={'request': request})
    serializer.data["items"].sort(key=lambda x: datetime.strptime(x["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"), reverse=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  
  def post(self, request, **kwargs):
    author = request.user
    target = request.data
    target_host = parse_url(target["host"]).host
    request_host = request.get_host().split(":")[0]
    if (target_host not in API_LOOKUP and target_host != request_host) or target["id"] == author.id:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    target_obj = get_or_create_user(target)
    request_data = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "summary": f"{author.username} wants to be your friend",
      "type": "Follow",
      "actor": AuthorRemoteSerializer(author, context={'request': request}).data,
      "object": AuthorRemoteSerializer(target_obj, context={'request': request}).data,
    }
    if target_obj.is_foreign:
      adapter = API_LOOKUP[target_host]
      resp = adapter.request_post_author_inbox(target_obj.id, request_data)
      if resp["status_code"] == 200:
        # since we don't know if a foreign target would accept the friend request, we record the follow relation first
        # then we will use /authors/{author_id}/followers/{foreign_author_id} to check if the target has accepted the request
        Follow.objects.create(target=target_obj, follower=author)
    else:
      handleInbox(target_obj, request_data)
      
    return Response(status=status.HTTP_200_OK)
  
  
class FriendRequestDetail(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [TokenAuthentication]
  queryset = FriendRequest.objects.all()
  serializer_class = FriendRequestListSerializer
  lookup_url_kwarg = "friend_request_id"
  
  
  def patch(self, request, **kwargs):
    author = request.user
    friend_request = self.get_object()
    
    if friend_request.target != author or friend_request.status != "PENDING":
      return Response(status=status.HTTP_403_FORBIDDEN)
    
    request_status = request.data.get("status", None)
    patch_data = {
      "status": request_status
    }
    
    serializer = FriendRequestSerializer(friend_request, data=patch_data, partial=True)
    if serializer.is_valid():
      serializer.save()
      if request_status == "ACCEPTED":
        Follow.objects.create(target=friend_request.target, follower=friend_request.requester)
      return Response(serializer.data, status=status.HTTP_200_OK)    
    
    return Response(status=status.HTTP_200_OK)
        