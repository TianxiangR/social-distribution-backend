from api.models import User, Post
from api.serializer import  PostDetailSerializer, PostListSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class PostListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.filter(visibility="PUBLIC")
    serializer_class = PostListSerializer
    
    
    def get(self, request, **kwargs):
        posts = self.get_queryset()
        serializer = self.get_serializer(posts, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PostDetailRemote(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.filter(visibility="PUBLIC")
  serializer_class = PostDetailSerializer
  

  def get(self, request, **kwargs):
    post = self.get_object()
    if post.visibility == 'PUBLIC':
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_404_NOT_FOUND)







