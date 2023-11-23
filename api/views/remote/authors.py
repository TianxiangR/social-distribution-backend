from api.models import User, Post, Comment
from api.serializers.cross_site_serializers import AuthorSerializer, PostSerializer, CommentSerializer, InboxSerializer
from api.serializer import LikePostSerializer, LikeCommentSerializer, FollowSerializer, CommentSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,get_object_or_404
from rest_framework import status
from dateutil.parser import parse
from api.utils import get_foreign_author_or_create, clip_id_from_url
from api.permissions import IsServer
from ...server_adapters.my_site_adapter import MySiteAdapter


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
  
class FollowerList(GenericAPIView):
  authentication_classes = [BasicAuthentication]
  permission_classes = [IsAuthenticated, IsServer]
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    author = get_object_or_404(User, pk=author_id)
    local_followings = author.following_relations.all()
    foreign_followings = author.foreign_following_relations.all()
    local_users = [following.following for following in local_followings]
    base_data = AuthorSerializer(local_users, many=True, context={'request': request}).data
    
    adapter = MySiteAdapter()
    for following in foreign_followings:
      id = clip_id_from_url(following.following)
      resp = adapter.request_get_author_detail(id)
      if resp['status_code'] == 200:
        base_data.append(resp['data'])
    
    response_body = {
      "type": "followers",
      "items": base_data
    }
    print("reached here")
    
    return Response(response_body, status=status.HTTP_200_OK)
    
  
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
  
  def get(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    author = get_object_or_404(User, pk=author_id)
    inboxes = author.inbox.filter(target=author)
    response_body = {
      "type": "inbox",
      "author": f"{request.scheme}://{request.get_host()}/authors/{author.id}",
      "items": []
    }
    
    for inbox in inboxes:
      if inbox.type == 'SHARE_POST':
        serializer = PostSerializer(inbox, context={'request': request})
        response_body['items'].append(serializer.data)
      elif inbox.type == 'FOLLOW':
        serializer = FollowSerializer(inbox, context={'request': request})
        response_body['items'].append(serializer.data)
      elif inbox.type == 'COMMENT':
        serializer = CommentSerializer(inbox, context={'request': request})
        response_body['items'].append(serializer.data)
      elif inbox.type == 'LIKE_POST':
        serializer = LikePostSerializer(inbox, context={'request': request})
        response_body['items'].append(serializer.data)
      elif inbox.type == 'LIKE_COMMENT':
        serializer = LikeCommentSerializer(inbox, context={'request': request})
        response_body['items'].append(serializer.data)
    return Response(response_body, status=status.HTTP_200_OK)
  
  def post(self, request, **kwargs):
    author_id = kwargs.get('author_id')
    request_body = request.data
    actor_data = request_body.get('actor')
    actor = get_foreign_author_or_create(actor_data)
    target = get_object_or_404(User, pk=author_id)
    type = request_body.get('type')   
    
    if type == "SHARE_POST":
      post_data = request_body.get('object')
      if post_data.get('host').includes(request.get_host()):
        post = get_object_or_404(Post, origin=post_data.get('id'))
      else:
        post = get_object_or_404(Post, foreign_id=post_data.get('id'))
      
      serializer = InboxSerializer(actor=actor, target=target, post=post, type=type)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    if type == "FOLLOW":
      follower = actor
      following = target
      follow_serializer = FollowSerializer(data={'follower': follower.id, 'following': following.id})
      if follow_serializer.is_valid():
        follow_serializer.save()
        follow_object = follow_serializer.instance
        serializer = InboxSerializer(actor=actor, target=target, follow=follow_object, type=type)
      else:
        return Response(follow_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    if type == 'COMMENT':
      comment_data = request_body.get('object')
      post_id = comment_data.get('post_id')
      post = get_object_or_404(Post, pk=post_id)
      comment_serializer = CommentSerializer(data={'user': actor.id, 'post': post.id, 'content': comment_data.get('comment')})
      if comment_serializer.is_valid():
        comment_serializer.save()
        comment_object = comment_serializer.instance
        serializer = InboxSerializer(actor=actor, target=target, comment=comment_object, type=type)
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if type == 'LIKE_POST':
      post_data = request_body.get('object')
      post_id = post_data.get('post_id')
      post = get_object_or_404(Post, pk=post_id)
      like_serializer = LikePostSerializer(data={'user': actor.id, 'post': post.id})
      if like_serializer.is_valid():
        like_serializer.save()
        like_object = like_serializer.instance
        serializer = InboxSerializer(actor=actor, target=target, like_post=like_object, type=type)
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    if type == 'LIKE_COMMENT':
      comment_data = request_body.get('object')
      comment_id = comment_data.get('comment_id')
      comment = get_object_or_404(Comment, pk=comment_id)
      like_serializer = LikeCommentSerializer(data={'user': actor.id, 'comment': comment.id})
      if like_serializer.is_valid():
        like_serializer.save()
        like_object = like_serializer.instance
        serializer = InboxSerializer(actor=actor, target=target, like_comment=like_object, type=type)
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

    
    
  
