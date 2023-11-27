from api.models import User, Post
from api.serializer import  PostDetailRemoteSerializer, PostListSerializer, PostBriefListSerializer, PostSerializer, PostDetailLocalSerializer, AuthorRemoteSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import has_access_to_post
import uuid
from datetime import datetime
from .inbox import handleInbox
from urllib3.util import parse_url
from ..api_lookup import API_LOOKUP


class PostListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.filter(visibility="PUBLIC")
    serializer_class = PostListSerializer
    
    
    def get(self, request, **kwargs):
        posts = self.get_queryset()
        serializer = self.get_serializer(posts, context = {'request': request})
        data = serializer.data
        
        for post in data["items"]:
          post["commentsSrc"]["comments"].sort(key=lambda x: datetime.strptime(x["published"], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=True)
        
        data["items"].sort(key=lambda x: datetime.striptime(x["published"], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=True)
          
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PostDetailRemote(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.filter(visibility="PUBLIC")
  serializer_class = PostDetailRemoteSerializer
  

  def get(self, request, **kwargs):
    post = self.get_object()
    if post.visibility == 'PUBLIC':
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
class PostListLocal(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = Post.objects.all()
  serializer_class = PostBriefListSerializer
  
  
  def get(self, request, **kwargs):
    requester = request.user
    posts = self.get_queryset()
    accessible_posts = []
    
    for post in posts:
      if has_access_to_post(post, requester):
        accessible_posts.append(post)
        
    serializer = self.get_serializer(accessible_posts, context = {'request': request})
    serializer.data["items"].sort(key=lambda x: datetime.strptime(x["published"], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
  def post(self, request, **kwargs):
    author = request.user
    post_data = request.data
    post_id = uuid.uuid4()
    post_data['author'] = author.id
    post_data['source'] = f"{request.scheme}://{request.get_host()}/authors/{author.id}/posts/{post_id}"
    post_data['origin'] = post_data['source']
    post_data['id'] = post_id
    
    serializer = PostSerializer(data=post_data, context = {'request': request})
    if serializer.is_valid():
      serializer.save()
      instance = serializer.instance
      for user in User.objects.filter(is_server=False, is_superuser=False):
        if user.id != author.id and has_access_to_post(instance, user):
          receiver_obj = user
          object = PostDetailRemoteSerializer(instance, context={'request': request}).data
          request_data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": f"{author.username} shared a post with you",
            "author": AuthorRemoteSerializer(author, context={'request': request}).data,
            "object": object,
          }
          if not user.is_foreign:
            try:
              handleInbox(receiver_obj, request_data)
            except:
              pass
          else:
            user_host = parse_url(user.host).host
            if user_host in API_LOOKUP:
              adapter = API_LOOKUP[user_host]
              adapter.request_post_author_inbox(user.id, request_data)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PostDetailLocal(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = Post.objects.all()
  serializer_class = PostDetailLocalSerializer
  lookup_url_kwarg = 'post_id'
  
  
  def get(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    if has_access_to_post(post, requester):
      serializer = self.get_serializer(post, context = {'request': request})
      serializer.data["commentsSrc"]["comments"].sort(key=lambda x: datetime.strptime(x["published"], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
  def put(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    if post.author == requester:
      serializer = PostSerializer(post, data=request.data, context = {'request': request})
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
      
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
  def patch(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    if post.author == requester:
      serializer = PostSerializer(post, data=request.data, partial=True, context = {'request': request})
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
      
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
  def delete(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    if post.author == requester:
      post.delete()
      return Response(status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  






