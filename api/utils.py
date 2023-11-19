from .models import User, Post, PostAccessPermission, Notification
from rest_framework.generics import get_object_or_404
from .models import Follow
from django.http import HttpResponseBadRequest
import uuid

def get_friends(user):
  user_followers_query = user.follower_relations.all()
  user_following_query = user.following_relations.all()
  
  user_followers_id = [user_follower.follower.id for user_follower in user_followers_query]
  user_following_id = [user_following.following.id for user_following in user_following_query]
  
  # object filter using list of keywords: https://stackoverflow.com/questions/5956391/django-objects-filter-with-list
  user_followers = User.objects.filter(id__in=user_followers_id)
  user_followings = User.objects.filter(id__in=user_following_id)
  
  friends = [user_follower for user_follower in user_followers if user_follower in user_followings]
  
  return friends
  

def get_visible_posts(user):
  myPosts = Post.objects.filter(author=user.id)
  public_posts = Post.objects.filter(visibility='public')
  friends = get_friends(user)
  friends_ids = [friend.id for friend in friends]
  friend_only_posts = Post.objects.filter(author__in=friends_ids, visibility='friend-only')   
  posts = set(myPosts | public_posts | friend_only_posts)        
  access_permissions = user.post_access_permissions.all()

  for access_permission in access_permissions:
      access_permission_post = access_permission.post
      posts.add(access_permission_post)
      
  return posts


def has_access_to_post(user, post):
  if post.visibility == 'public':
    return True
  elif post.visibility == 'friend-only':
    friends = get_friends(user)
    return post.author in friends
  else:
    access_permissions = user.post_access_permissions.all()
    return post in [access_permission.post for access_permission in access_permissions]


def create_access_permission(user, post):
  author = post.author
  try:
    author_follow_relation = Follow.objects.get(follower=author, following=user)
    target_follow_relation = Follow.objects.get(follower=user, following=author)
    PostAccessPermission.objects.create(user=user, post=post, author_follow_relation=author_follow_relation, target_follow_relation=target_follow_relation)
  except Follow.DoesNotExist:
    raise HttpResponseBadRequest('User {} is not following {}'.format(user.username, author.username))
  

def update_access_permission(post, new_permitted_user_list):
  previous_access_permissions = post.post_access_permissions.all()
  removed_access_permissions = [access_permission for access_permission in previous_access_permissions if access_permission.user not in new_permitted_user_list]
  new_access_permissions = [user for user in new_permitted_user_list if user not in [access_permission.user for access_permission in previous_access_permissions]]
  
  for access_permission in removed_access_permissions:
    access_permission.delete()
  
  for user in new_access_permissions:
    create_access_permission(user, post)
    Notification.objects.create(user=user, author=post.author, post=post, type='SHARE_POST')
    

def has_access_to_comment(user, comment):
  if comment.post.visibility == 'public':
    return True
  
  # post author's comment can be seen by everyone who has access to the post
  # users that are not the author of the post can see their own comments and the post author's comment
  return comment.post.author == user or comment.user == user or comment.post.author == comment.user


def get_foreign_author_or_create(author):
  author_id = author.get('id', None)
  try:
    author = User.objects.get(id=author_id)
  except User.DoesNotExist:
    author = User.objects.create_user(id=uuid.uuid4(), username=author['displayName'], password='password', host=author['host'], is_foreign=True, foreign_profile_image=author['profileImage']) 
    author.save()
  return author
    