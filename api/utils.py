from .models import User, Post, Comment, PostAccess
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ParseError
import uuid
import re
from datetime import datetime

def is_comment_detail_url(url):
  return re.search(r'^https?:\/\/.+\/authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/comments/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})$', url) is not None
  
  
def is_post_detail_url(url):
  return re.search(r"^https?:\/\/.+\/authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})$", url) is not None
  
  
def get_post_id_from_url(url):
  result =  re.search("posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    raise ParseError("Invalid post url")
  return result.group(1)


def get_author_id_from_url(url):
  result =  re.search("authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    raise ParseError("Invalid author url")
  return result.group(1)


def get_comment_id_from_url(url):
  result = re.search("comments\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    raise ParseError("Invalid comment url")
  return result.group(1)


def get_or_create_foreign_user(obj):
  id = get_author_id_from_url(obj["id"])
  if User.objects.filter(id=id).exists():
    return User.objects.get(id=id)
  else:
    user = User.objects.create(
      id=id,
      username=obj["displayName"],
      email="default@email.com",
      password="default",
      host = obj["host"],
      url = obj["url"],
      github = obj["github"],
      is_foreign = True,
      image_url = obj["profileImage"]
    )
    user.save()
    return user
  
  
def create_comment_from_request_data(request_data, post_obj):
  author = request_data.get('author', None)
  author_obj = get_or_create_foreign_user(author)
  comment = request_data.get('comment', None)
  published = request_data.get('published', None)
  id = request_data.get('id', None)
  comment_id = get_comment_id_from_url(id)
  comment_obj =  Comment.objects.create(id=comment_id, post=post_obj, user=author_obj, comment=comment, created_at=datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%f%z'))
  return comment_obj


def create_or_update_shared_post_from_request_data(request_data, receiver_obj):
  id = request_data.get('id', None)
  title = request_data.get('title', None)
  source = request_data.get('source', None)
  origin = request_data.get('origin', None)
  contentType = request_data.get('contentType', None)
  content = request_data.get('content', None)
  author = request_data.get('author', None)
  visibility = request_data.get('visibility', None)
  unlisted = request_data.get('unlisted', None)
  published = request_data.get('published', None)
  commentsSrc = request_data.get('commentsSrc', None)
  comments = []
  if commentsSrc is not None:
    comments = commentsSrc.get('comments', [])
  post_id = get_post_id_from_url(id)
  
  
  if Post.objects.filter(id=post_id).exists():
    post_obj = Post.objects.get(id=post_id)
    post_obj.title = title
    post_obj.source = source
    post_obj.origin = origin
    post_obj.contentType = contentType
    post_obj.content = content
    post_obj.visibility = visibility
    post_obj.unlisted = unlisted
    post_obj.created_at = datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%f%z')
    post_obj.save()
    return post_obj

  author_obj = get_or_create_foreign_user(author)
  post_obj = Post.objects.create(id=post_id, title=title, source=source, origin=origin, content=content, contentType=contentType, author=author_obj, visibility=visibility, unlisted=unlisted, created_at=datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%f%z'), is_foreign=True)
  post_obj.save()
  
  PostAccess.objects.create(post=post_obj, user=receiver_obj)
  
  for comment in comments:
    create_comment_from_request_data(comment, post_obj)
  
  return post_obj