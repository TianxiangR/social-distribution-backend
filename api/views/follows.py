from api.models import User
from api.serializer import AuthorRemoteSerializer, AuthorListLocalSerializer, AuthorLocalSerializer, AuthorListRemoteSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..api_lookup import API_LOOKUP
from ..server_adapters.base_server_adapter import BaseServerAdapter
from ..utils import get_author_id_from_url
from rest_framework.exceptions import ParseError
from ..api_lookup import API_LOOKUP
from urllib3.util import parse_url

class FollowerListLocal(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [TokenAuthentication]
  serializer_class = AuthorListLocalSerializer
  queryset = User.objects.filter(is_server=False, is_superuser=False)
  
  
  def get(self, request, **kwargs):
    author = request.user
    followers = []
    for following_relation in author.followed_relations.all():
      followers.append(following_relation.follower)
    
    serializer  = self.get_serializer(followers, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class FollowerListRemote(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [BasicAuthentication]
  serializer_class = AuthorListRemoteSerializer
  lookup_url_kwarg = 'author_id'
  queryset = User.objects.filter(is_server=False, is_superuser=False)
  
  
  def get(self, request, **kwargs):
    author = self.get_object()
    followers = []
    for following_relation in author.followed_relations.all():
      followers.append(following_relation.follower)
    
    serializer  = self.get_serializer(followers, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
class FollowingListLocal(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [TokenAuthentication]
  serializer_class = AuthorListLocalSerializer
  queryset = User.objects.all()
  
  
  def get(self, request, **kwargs):
    author = request.user
    following = []
    for following_relation in author.following_relations.all():
      if not following_relation.target.is_foreign:
        following.append(following_relation.target)
      else:
        user_host = parse_url(following_relation.target.host).host
        if user_host in API_LOOKUP:
          adapter = API_LOOKUP[user_host]
          resp = adapter.request_get_author_following_check(following_relation.target.id, author.id)
          if resp["status_code"] == 200:
            following.append(following_relation.target)

    serializer  = self.get_serializer(following, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
class FollowDetailRemote(GenericAPIView):
  permission_classes = [IsAuthenticated]
  authentication_classes = [BasicAuthentication]
  serializer_class = AuthorRemoteSerializer
  lookup_url_kwarg = 'author_id'
  queryset = User.objects.filter(is_server=False, is_superuser=False)
  
  
  def get(self, request, **kwargs):
    author = self.get_object()
    foreign_id = kwargs.get('foreign_id', None)
    foreign_author = get_object_or_404(User, id=foreign_id)
    if foreign_author in author.following_relations.all():
      return Response(status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)