from ..models import User, Post
from api.serializer import AuthorRemoteSerializer, AuthorListLocalSerializer, AuthorLocalSerializer, AuthorListRemoteSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..api_lookup import API_LOOKUP
from ..server_adapters.base_server_adapter import BaseServerAdapter
from django.http.response import HttpResponse
from ..utils import get_author_id_from_url
from rest_framework.exceptions import ParseError
from ..api_lookup import API_LOOKUP
from urllib3.util import parse_url
import base64

class PostImage(GenericAPIView):
  lookup_url_kwarg = 'post_id'
  queryset = Post.objects.all()
  
  def get(self, request, **kwargs):
    post = self.get_object()
    
    try:
      image = post.image
      image_type = image.split(';')[0].split(":")[1]
      base64_data = image.split(',')[1]
      image_binary = base64.b64decode(base64_data)
      return HttpResponse(image_binary, content_type=image_type)
    except:
      return HttpResponse(status=status.HTTP_404_NOT_FOUND)
  
  
class ProfileImage(GenericAPIView):
  lookup_url_kwarg = 'author_id'
  queryset = User.objects.all()
  
  def get(self, request, **kwargs):
    author = self.get_object()
    try:
      image = author.profile_image
      image_type = image.split(';')[0].split(":")[1]
      base64_data = image.split(',')[1]
      image_binary = base64.b64decode(base64_data)
  
      return HttpResponse(image_binary, content_type=image_type)
    except Exception as e:
      print(e)
      return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    