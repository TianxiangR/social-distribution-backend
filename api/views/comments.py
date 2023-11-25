from api.models import User, Post
from api.serializer import CommentDetailSerializer, CommentListSerializer
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class CommentListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'post_id'
    queryset = Post.objects.all().filter(visibility="PUBLIC")
    serializer_class = CommentListSerializer
    
    
    def get(self, request, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post.comments.all(), context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CommentDetailRemote(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.all().filter(visibility="PUBLIC")
  serializer_class = CommentDetailSerializer
  
  
  def get(self, request, **kwargs):
    post = self.get_object()
    comment_id = kwargs.get('comment_id')
    comment = post.comments.filter(id=comment_id).first()
    if comment:
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
        
        
        
        