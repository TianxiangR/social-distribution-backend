from api.models import User, Post, Comment
from api.serializer import CommentDetailRemoteSerializer, CommentListRemoteSerializer, CommentListLocalSerializer, CommentSerializer, AuthorRemoteSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils import has_access_to_post
from urllib3.util import parse_url
from ..api_lookup import API_LOOKUP
from .inbox import handleInbox
from drf_spectacular.utils import extend_schema

@extend_schema(
    description="Get a list of comments of a post from the server",
    responses={200: CommentListRemoteSerializer}
)
class CommentListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'post_id'
    queryset = Post.objects.all().filter(visibility="PUBLIC")
    serializer_class = CommentListRemoteSerializer
    
    
    def get(self, request, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post.comments.all(), context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    description="Get the comment information from the server by id",
    responses={200: CommentDetailRemoteSerializer}
)
class CommentDetailRemote(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.all().filter(visibility="PUBLIC")
  serializer_class = CommentDetailRemoteSerializer
  
  
  def get(self, request, **kwargs):
    post = self.get_object()
    comment_id = kwargs.get('comment_id')
    comment = post.comments.filter(id=comment_id).first()
    if comment:
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
class CommentListLocal(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.all()
  serializer_class = CommentListLocalSerializer
  
  
  def get(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    comments = post.comments.all()
    accessible_comments = []
    
    if has_access_to_post(post, requester):
      for comment in comments:
        if comment.user == requester or comment.user == post.author or post.visibility == "PUBLIC":
          accessible_comments.append(comment)
    
    serializer = self.get_serializer(accessible_comments, context = {'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
  def post(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    if has_access_to_post(post, requester):
      comment = request.data.get('comment', None)
      if comment:
        comment_data = {
          "user": requester.id,
          "content": comment,
          "post": post.id,
        }
        
        serializer = CommentSerializer(data=comment_data)
        if serializer.is_valid():
          serializer.save()
          request_data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "comment",
            "author": AuthorRemoteSerializer(requester, context={'request': request}).data,
            "object": CommentDetailRemoteSerializer(serializer.instance, context={'request': request}).data,
          }
          if not post.is_foreign:
            handleInbox(post.author, request_data)
          else:
            post_author_host = parse_url(post.author.host).host
            if post_author_host in API_LOOKUP:
              adapter = API_LOOKUP[post_author_host]
              adapter.request_post_author_inbox(post.author.id, request_data)
          return Response(serializer.data, status=status.HTTP_200_OK)
        else:
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_403_FORBIDDEN)
        
        
        