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
from ..utils import get_author_id_from_url, get_or_create_user, get_post_id_from_url
from drf_spectacular.utils import extend_schema
import requests
from logging import getLogger
from datetime import datetime
from dateutil.parser import parse as date_parser
from urllib3.util import parse_url
import pytz

logger = getLogger('django')
utc = pytz.UTC

def get_datetime_from_str(s: str) -> datetime:
  dt = date_parser(s)
  if dt.tzinfo is None:
    return utc.localize(dt)
  return dt

@extend_schema(
    description="Get a list of public posts of an author from the server",
    responses={200: PostListSerializer}
)
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
          post["commentsSrc"]["comments"].sort(key=lambda x: get_datetime_from_str(x["published"]), reverse=True)
        
        data["items"].sort(key=lambda x: get_datetime_from_str(x["published"]), reverse=True)
          
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    description="Get the post information from the server by id",
    responses={200: PostDetailRemoteSerializer}
)
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
  queryset = Post.objects.filter(unlisted=False)
  serializer_class = PostBriefListSerializer
  
  
  def get(self, request, **kwargs):
    requester = request.user
    posts = self.get_queryset()
    accessible_posts = []
    
    for post in posts:
      if has_access_to_post(post, requester):
        accessible_posts.append(post)
        
    serializer = self.get_serializer(accessible_posts, context = {'request': request})
    
    # for adapter in API_LOOKUP.values():
    #   try:
    #     author_resp = adapter.request_get_author_list()
    #     if author_resp["status_code"] == 200:
    #       for author in author_resp["body"]:
    #         author["id"] = get_author_id_from_url(author["id"])
    #         post_resp = adapter.request_get_author_posts(author["id"])
    #         if post_resp["status_code"] == 200:
    #           for post_data in post_resp["body"]:
    #             post_data["id"] = get_post_id_from_url(post_data["id"])
    #             post_data["author"]["id"] = get_author_id_from_url(post_data["author"]["id"])
    #             post_data["author"]["host"] = parse_url(post_data["author"]["host"]).host
    #             post_data["is_foreign"] = True
    #             serializer.data["items"].append(post_data)
    #   except Exception as e:
    #     logger.error(f"ERROR [{datetime.now()}] {e}")
    
    # github activity
    user = User.objects.get(id=requester.id)
    github_activity_data = []
    if user.github is not None:
      github_username = user.github.split('/')[-1]
      response = requests.get('https://api.github.com/users/{}/events'.format(github_username))

      if response.status_code == 200:
        github_activity_data = response.json()
        for event in github_activity_data:
          if 'created_at' in event:
              event['published'] = event.pop('created_at')
      else:
        logger.error(f"ERROR [{datetime.now()}] Github API call failed with status code {response.status_code}")
  
    combined_data = {
      "items": serializer.data["items"] + github_activity_data,
    }
    
    combined_data["items"].sort(key=lambda x: get_datetime_from_str(x["published"]), reverse=True)
    
    return Response(combined_data, status=status.HTTP_200_OK)

  
  def post(self, request, **kwargs):
    author = request.user
    post_data = request.data
    post_id = uuid.uuid4()
    post_data['id'] = post_id
    post_data['author'] = author.id
    post_data['origin'] = f"{request.scheme}://{request.get_host()}/author/{author.id}/posts/{post_id}"
    post_data['source'] = f"{request.scheme}://{request.get_host()}/author/{author.id}/posts/{post_id}"
    
    serializer = PostSerializer(data=post_data, context = {'request': request})
    if serializer.is_valid():
      instance = serializer.save()
      object = dict(PostDetailRemoteSerializer(instance, context={'request': request}).data)
      request_data = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": f"{author.username} shared a post with you",
        "object": object,
      }
    
      followers = [followed_relation.follower for followed_relation in author.followed_relations.all()]
      for user in followers:
        if not user.is_foreign:
          receiver_obj = user
          try:
            handleInbox(receiver_obj, object)
          except:
            pass
      
      if instance.unlisted == False:
        for adapter in API_LOOKUP.values():
          if instance.visibility == "FRIENDS":
            for follower in followers:
              host = parse_url(follower.host).host
              if host in API_LOOKUP:
                adapter.request_post_author_inbox(follower.id, request_data)
          elif instance.visibility == "PUBLIC":
            try:
              author_list_resp = adapter.request_get_author_list()
              if author_list_resp["status_code"] == 200:
                for foreign_author in author_list_resp["body"]:
                  foreign_author_id = get_author_id_from_url(foreign_author["id"])
                  adapter.request_post_author_inbox(foreign_author_id, request_data)
            except Exception as e:
              logger.error(f"ERROR [{datetime.now()}] {e}")
                
          return Response(serializer.data, status=status.HTTP_200_OK)
      else:
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
    host = request.query_params.get("host", None)
    author_id = request.query_params.get("author_id", None)
    if host is not None and author_id is not None:
      if host in API_LOOKUP:
        resp = API_LOOKUP[host].request_get_author_post_detail(author_id, kwargs["post_id"])
        if resp["status_code"] == 200:
          return Response(resp["body"], status=status.HTTP_200_OK)
    
    post = self.get_object()
    if has_access_to_post(post, requester):
      serializer = self.get_serializer(post, context = {'request': request})
      serializer.data["commentsSrc"]["comments"].sort(key=lambda x: get_datetime_from_str(x["published"]), reverse=True)
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


class SharePost(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  
  def post(self, request, **kwargs):
    author = request.user
    targets = request.data["targets"]
    post_data = request.data["post"]
    if post_data["visibility"] == "PUBLIC":
      if Post.objects.filter(id=post_data["id"], is_foreign=False).exists():
        post_obj = Post.objects.get(id=post_data["id"])
        post_data = PostDetailRemoteSerializer(post_obj, context={'request': request}).data
      else:
        host = parse_url(post_data["author"]["host"]).host
        if host in API_LOOKUP:
          adapter = API_LOOKUP[host]
          resp = adapter.request_get_author_post_detail(post_data["author"]["id"], post_data["id"])
          if resp["status_code"] == 200:
            post_data = resp["body"]
    else:
      post_obj = Post.objects.filter(id=post_data["id"]).first()
      if post_obj:
        post_data = PostDetailRemoteSerializer(post_obj, context={'request': request}).data
      else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    for user_data in targets:
      user = get_or_create_user(user_data)
      if user and user.id != author.id:
        request_data = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "summary": f"{author.username} shared a post with you",
          "object": post_data,
        }
        host = parse_url(user.host).host
        if not user.is_foreign:
          handleInbox(user, post_data)
        elif host in API_LOOKUP:
          adapter = API_LOOKUP[host]
          try:
            adapter.request_post_author_inbox(user.id, post_data)
          except Exception as e:
            logger.error(f"ERROR [{datetime.now()}] {e}")
          
    return Response(status=status.HTTP_200_OK)     
  
  
class UnlistedPostListLocal(GenericAPIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  queryset = Post.objects.filter(unlisted=True)
  serializer_class = PostBriefListSerializer
  
  def get(self, request, **kwargs):
    requester = request.user
    posts = self.get_queryset().filter(author=requester)
        
    serializer = self.get_serializer(posts, context = {'request': request})
    serializer.data["items"].sort(key=lambda x: get_datetime_from_str(x["published"]), reverse=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  

class UnlistedPostDetailLocal(GenericAPIView):
  queryset = Post.objects.filter(unlisted=True)
  serializer_class = PostDetailLocalSerializer
  lookup_url_kwarg = 'post_id'
  
  def get(self, request, **kwargs):
    post = self.get_object()
    serializer = self.get_serializer(post, context = {'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
  






