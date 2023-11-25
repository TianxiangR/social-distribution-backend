from api.models import User
from api.serializer import AuthorSerializer, AuthorListSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class AuthorListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = AuthorListSerializer
    
    def get(self, request, **kwargs):
        users = self.get_queryset().filter(is_server=False, is_superuser=False, is_foreign=False)
        serializer = self.get_serializer(users, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorDetail(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'author_id'
  queryset = User.objects.all()
  serializer_class = AuthorSerializer
  
  
  def get(self, request, **kwargs):
    author = self.get_object()
    serializer = self.get_serializer(author)
    return Response(serializer.data, status=status.HTTP_200_OK)