from api.models import User
from api.serializer import AuthorRemoteSerializer, AuthorListLocalSerializer, AuthorLocalSerializer, AuthorListRemoteSerializer, UserSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..api_lookup import API_LOOKUP
from ..server_adapters.base_server_adapter import BaseServerAdapter
from ..utils import get_author_id_from_url
from rest_framework.exceptions import ParseError

class AuthorListRemote(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = AuthorListRemoteSerializer


    def get(self, request, **kwargs):
        users = self.get_queryset().filter(is_server=False, is_superuser=False, is_foreign=False)
        serializer = self.get_serializer(users, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorDetailRemote(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'author_id'
  queryset = User.objects.filter(is_server=False, is_superuser=False, is_foreign=False)
  serializer_class = AuthorRemoteSerializer
  
  
  def get(self, request, **kwargs):
    author = self.get_object()
    serializer = self.get_serializer(author)
    return Response(serializer.data, status=status.HTTP_200_OK)
  

class AuthorDetailLocal(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  queryset = User.objects.filter(is_server=False, is_superuser=False)
  authentication_classes = [TokenAuthentication]
  serializer_class = AuthorLocalSerializer
  lookup_url_kwarg = 'author_id'
  
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    if self.get_queryset().filter(id=author_id).exists():
      user = self.get_object()
      serializer = self.get_serializer(user)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    host = request.query_params.get('host')
    if host in API_LOOKUP:
      adapter = API_LOOKUP[host]
      resp = adapter.request_get_author_detail(author_id)
      if resp["status_code"] == 200:
        resp["body"]["id"] = get_author_id_from_url(resp["body"]["id"])
        return Response(resp["body"], status=status.HTTP_200_OK)
      
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  
class AuthorListLocal(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = AuthorListLocalSerializer


    def get(self, request, **kwargs):
        users = self.get_queryset().filter(is_server=False, is_superuser=False, is_foreign=False).exclude(id=request.user.id)
        serializer = self.get_serializer(users, context = {'request': request})
        response_data = serializer.data
        
        for adapter in API_LOOKUP.values():
          resp = adapter.request_get_author_list()
          if resp["status_code"] == 200:
            resp_data = resp["body"]
            for author in resp_data:
              try:
                author_id = get_author_id_from_url(author["id"])
                author["id"] = author_id
                resp  = adapter.request_get_author_following_check(author_id, request.user.id)
                if resp["status_code"] == 200:
                  author["is_following"] = True
                else:
                  author["is_following"] = False
                response_data["items"].append(author)
              except ParseError:
                pass
        
        return Response(response_data, status=status.HTTP_200_OK)
      
      
class Profile(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = User.objects.all()
  serializer_class = AuthorLocalSerializer
  
  
  def get(self, request, **kwargs):
    user = request.user
    serializer = self.get_serializer(user, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
  def patch(self, request, **kwargs):
    user = request.user
    username = request.data.get('username', None)
    github = request.data.get('github', None)
    update_data = {
      "username": username,
      "github": github
    }
    
    serializer = UserSerializer(user, data=update_data, partial=True)
    
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    