from api.models import User, Post, InboxItem, FriendRequest, LikePost, LikeComment, Comment, Follow
from api.serializer import AuthorLocalSerializer, AuthorRemoteSerializer, FriendRequestSerializer, FriendRequestDetailSerializer, FriendRequestListSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import get_or_create_user, is_comment_detail_url,  get_post_id_from_url, get_comment_id_from_url, is_post_detail_url, create_or_update_shared_post_from_request_data, create_comment_from_request_data
import json
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
    return Response(serializer.data, status=status.HTTP_200_OK)
  