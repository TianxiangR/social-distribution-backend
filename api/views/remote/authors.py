from api.models import User, Post, Comment, Inbox, PostAccessPermission
from api.serializers.cross_site_serializers import AuthorSerializer, PostSerializer, CommentSerializer, InboxSerializer
from api.serializer import LikePostSerializer, LikeCommentSerializer, FollowSerializer, InboxSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,get_object_or_404
from rest_framework import status
from dateutil.parser import parse
from api.utils import get_foreign_author_or_create, clip_id_from_url
from api.permissions import IsServer
from ...server_adapters.my_site_adapter import MySiteAdapter
from urllib3.util.url import parse_url
import requests


class AuthorList(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  queryset = User.objects.all()
  serializer_class = AuthorSerializer
  
  def get(self, request, **kwargs):
    authors = self.get_queryset()
    authors = authors.filter(is_server=False, is_superuser=False)
    serializer = self.get_serializer(authors, many=True, context={'request': request})
    response_body = {
      "type": "authors",
      "items": serializer.data
    }
    
    return Response(response_body, status=status.HTTP_200_OK)


class AuthorDetail(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  queryset = User.objects.all()
  serializer_class = AuthorSerializer
  lookup_url_kwarg = 'author_id'
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    author = get_object_or_404(self.get_queryset(), pk=author_id)
    if author.is_server:
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = self.get_serializer(author, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorPostList(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    print(author_id)
    author = get_object_or_404(User, pk=author_id)
    posts = author.posts.all()
    print(len(posts))
    response_body = {
      "type": "posts",
      "items": []
    }
    items = PostSerializer(posts, many=True, context={'request': request}).data
    items.sort(key=lambda x: parse(x['published']), reverse=True)
    response_body['items'] = items
    
    return Response(response_body, status=status.HTTP_200_OK)


class AuthorPostDetail(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    post_id = kwargs.get('post_id')
    author = get_object_or_404(User, pk=author_id)
    post = get_object_or_404(author.posts.all(), pk=post_id)
    serializer = PostSerializer(post, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

 
class AuthorPostCommentList(GenericAPIView):  
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    post_id = kwargs.get('post_id')
    author = get_object_or_404(User, pk=author_id)
    post = get_object_or_404(author.posts.all(), pk=post_id)
    comment = post.comments.all()
    serializer = CommentSerializer(comment, many=True, context={'request': request})
    response_body = {
      "type": "comments",
      "comments": serializer.data,
      "post": str(post.origin),
      "id": str(post.origin) + '/comments',
    }
    
    response_body['comments'].sort(key=lambda x: parse(x['published']), reverse=True)
    
    return Response(response_body, status=status.HTTP_200_OK)

  
class AuthorInboxList(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  
  
  def post(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    request_body = request.data
    target = get_object_or_404(User, pk=author_id)
    type = request_body.get('type', None)
    object_url = None
    
    if type == "post":
      object_url = request_body.get('origin', None)
      PostAccessPermission.objects.create(user=target, post=object_url)
    elif type == "comment":
      cotent = request_body.get('comment', None)
      Comment.objects.create(user=target, post=object_url, content=cotent)
      
      

    
    
  

