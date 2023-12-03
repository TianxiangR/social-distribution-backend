from api.models import User, Post, InboxItem, FriendRequest, LikePost, LikeComment, Comment, Follow
from api.serializer import InboxSerializer, AuthorRemoteSerializer, InboxRequestSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import get_or_create_user, is_comment_detail_url,  get_post_id_from_url, get_comment_id_from_url, is_post_detail_url, create_or_update_shared_post_from_request_data, create_comment_from_request_data, is_uuid
import json
from datetime import datetime
from drf_spectacular.utils import extend_schema, inline_serializer


def handleInbox(receiver_obj, request_data):
  type = request_data.get('type', None)
  sender_data = None
  sender_obj = None
  object = None
  
  if type is not None:
    sender_data = request_data.get('actor', None)
    if sender_data is None:
      sender_data = request_data.get('author', None)
    sender_obj = get_or_create_user(sender_data)
    object = request_data.get('object', None)

  print('reached here')
  print(type)
  if type == "Follow":
    if sender_obj:
      if not Follow.objects.filter(target=receiver_obj, follower=sender_obj).exists() \
        and (not FriendRequest.objects.filter(target=receiver_obj, requester=sender_obj).exists() \
          or FriendRequest.objects.filter(target=receiver_obj, requester=sender_obj).first().status != "PENDING"):
        FriendRequest.objects.create(target=receiver_obj, requester=sender_obj)
        InboxItem.objects.create(receiver=receiver_obj, type=type, sender=sender_obj, item=json.dumps(request_data))
        return Response(status=status.HTTP_200_OK)
    
  elif type == "Like":
    if is_comment_detail_url(object):
      comment_id = get_comment_id_from_url(object)
      comment_obj = Comment.objects.filter(id=comment_id).first()
      if comment_obj:
        LikeComment.objects.create(comment=comment_obj, user=sender_obj)
        InboxItem.objects.create(receiver=receiver_obj, sender=sender_obj, type=type, item=json.dumps(request_data))
        return Response(status=status.HTTP_200_OK)
    elif is_post_detail_url(object):
      post_id = get_post_id_from_url(object)
      post_obj = Post.objects.filter(id=post_id).first()
      print(post_obj)
      if post_obj:
        LikePost.objects.create(post=post_obj, user=sender_obj)
        InboxItem.objects.create(receiver=receiver_obj, sender=sender_obj, type=type, item=json.dumps(request_data))
        return Response(status=status.HTTP_200_OK)
    else:
      print("Invalid Like object")
  
  elif type == "comment":
    post_id = get_post_id_from_url(object["id"])
    post_obj = Post.objects.filter(id=post_id).first()
    object = request_data.get('object', None)
    if post_obj:
      create_comment_from_request_data(object, post_obj)
      InboxItem.objects.create(receiver=receiver_obj, sender=sender_obj, type=type, item=json.dumps(request_data))
      return Response(status=status.HTTP_200_OK)
    
  elif type == "post":
    print("reached here")
    create_or_update_shared_post_from_request_data(request_data, receiver_obj)
    InboxItem.objects.create(receiver=receiver_obj, sender=sender_obj, type=type, item=json.dumps(request_data))
    return Response(status=status.HTTP_200_OK)
    
        
  return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Get the inbox of the author",
    request=InboxRequestSerializer(),
)
class InboxListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'author_id'
    queryset = User.objects.all().filter(is_server=False, is_superuser=False, is_foreign=False)
    serializer_class = InboxSerializer
    
    
    def post(self, request, **kwargs):
        receiver_obj = self.get_object()

        return handleInbox(receiver_obj, request.data)
          
            
          