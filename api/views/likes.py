from api.models import User, Post, Comment, LikePost, LikeComment
from api.serializer import AuthorListRemoteSerializer, AuthorListLocalSerializer, LikePostSerializer, LikeCommentSerializer, AuthorRemoteSerializer, PostDetailRemoteSerializer, CommentDetailRemoteSerializer
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
    description="Get a list of likes of a post from the server",
    responses={200: AuthorListRemoteSerializer}
)
class LikePostListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'post_id'
    queryset = Post.objects.all().filter(visibility="PUBLIC", is_foreign=False)
    serializer_class = AuthorListRemoteSerializer
    
    
    def get(self, request, **kwargs):
        post = self.get_object()
        post_likes = post.likes.all()
        authors = []
        
        for post_like in post_likes:
          authors.append(post_like.user)
          
        serializer = self.get_serializer(authors, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
      

@extend_schema(
    description="Get a list of likes of a comment from the server",
    responses={200: AuthorListRemoteSerializer}
)
class LikeCommentListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'post_id'
    queryset = Post.objects.all().filter(visibility="PUBLIC", is_foreign=False)
    serializer_class = AuthorListRemoteSerializer
    
    
    def get(self, request, **kwargs):
      comment_id = kwargs.get('comment_id')
      comment = get_object_or_404(Comment, id=comment_id)
      if comment:
        comment_likes = comment.likes.all()
        authors = []
        
        for comment_like in comment_likes:
          authors.append(comment_like.user)
          
        serializer = self.get_serializer(authors, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
      
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    
class LikePostListLocal(LikePostListRemote):
  authentication_classes = [TokenAuthentication]
  queryset = Post.objects.all()
  serializer_class = AuthorListLocalSerializer
  
  
  def get(self, request, **kwargs):
    requester = get_object_or_404(User, id=request.user.id)
    post = self.get_object()
    
    if post.is_foreign:
      post_author = post.author
      post_author_host = parse_url(post_author.host).host
      if post_author_host in API_LOOKUP:
        adapter = API_LOOKUP[post_author_host]
        resp = adapter.request_get_author_post_likes(post_author.id, post.id)
        if resp["status_code"] == 200:
          return Response(resp["body"], status=status.HTTP_200_OK)
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    if has_access_to_post(post, requester):
      super().get(request, **kwargs)
      
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
  def post(self, request, **kwargs):
    requester = get_object_or_404(User, id=request.user.id)
    post = self.get_object()
    author_data = AuthorRemoteSerializer(requester, context={'request': request}).data
    request_data = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "summary": f"{requester.username} liked your post",
      "type": "Like",
      "object": f"{request.scheme}://{request.get_host()}/authors/{post.author.id}/posts/{post.id}",
      "author": author_data,
    }
    if post.is_foreign:
      post_author = post.author
      post_author_host = parse_url(post_author.host).host
      LikePost.objects.create(post=post, user=requester)
      if post_author_host in API_LOOKUP:
        adapter = API_LOOKUP[post_author_host]
        resp = adapter.request_post_author_inbox(post_author.id, request_data)
        return Response(status=status.HTTP_200_OK)
    
    if has_access_to_post(post, requester):
      serializer = LikePostSerializer(data={'user': requester.id, 'post': post.id})
      if serializer.is_valid():
        handleInbox(post.author, request_data)
        return Response(status=status.HTTP_200_OK)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
class LikeCommentListLocal(LikeCommentListRemote):
  authentication_classes = [TokenAuthentication]
  queryset = Post.objects.all()
  serializer_class = AuthorListLocalSerializer
  
  
  def get(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    comment_id = kwargs.get('comment_id')
    
    if post.is_foreign:
      post_author = post.author
      post_author_host = parse_url(post_author.host).host
      if post_author_host in API_LOOKUP:
        adapter = API_LOOKUP[post_author_host]
        resp = adapter.request_get_author_post_comment_likes(post_author.id, post.id, comment_id)
        if resp["status_code"] == 200:
          return Response(resp["body"], status=status.HTTP_200_OK)
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    if has_access_to_post(post, requester):
      super().get(request, **kwargs)
      
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
  def post(self, request, **kwargs):
    requester = request.user
    post = self.get_object()
    comment_id = kwargs.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id)
    
    comment_author = comment.user
    comment_author_host = parse_url(comment_author.host).host
    
    author_data = AuthorRemoteSerializer(requester, context={'request': request}).data
    request_data = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "summary": f"{requester.username} liked your comment",
      "type": "Like",
      "object": f"{request.scheme}://{request.get_host()}/authors/{comment_author.id}/posts/{post.id}/comments/{comment.id}",
      "author": author_data,
    }
    
    request_host = request.get_host().split(":")[0]
    if comment_author_host is not None and comment_author_host != request_host:
      LikeComment.objects.create(comment=comment, user=requester)
      if comment_author_host in API_LOOKUP:
        adapter = API_LOOKUP[comment_author_host]

        resp = adapter.request_post_author_inbox(comment_author.id, request_data)
        return Response(status=status.HTTP_200_OK)
    
    if has_access_to_post(post, requester):
      serializer = LikeCommentSerializer(data={'user': requester.id, 'comment': comment.id})
      if serializer.is_valid():
        handleInbox(comment_author, request_data)
        return Response(status=status.HTTP_200_OK)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_404_NOT_FOUND)