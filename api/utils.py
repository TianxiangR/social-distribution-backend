from .models import User, Post, Comment, PostAccess
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ParseError
import uuid
import re
from dateutil.parser import parse as parse_time

def is_comment_detail_url(url):
  return re.search(r'^https?:\/\/.+\/authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/comments\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})$', url) is not None \
    or re.search(r'^https?:\/\/.+\/authors\/([0-9|a-z|]{32})\/posts\/([0-9|a-z|]{32})\/comments\/([0-9|a-z|]{32})$', url) is not None
  
  
def is_post_detail_url(url):
  return re.search(r"^https?:\/\/.+\/authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})\/posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})$", url) is not None \
    or re.search(r"^https?:\/\/.+\/authors\/([0-9|a-z|]{32})\/posts\/([0-9|a-z|]{32})$", url) is not None


def is_uuid(str):
  try:
    uuid.UUID(str)
    return True
  except:
    return False

  
def get_post_id_from_url(url):
  result =  re.search("posts\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    result = re.search("posts\/([0-9|a-z|]{32})", url)
    if result is None:
      raise ParseError("Invalid post url")
  uuid_str = result.group(1)
  return str(uuid.UUID(uuid_str))


def get_author_id_from_url(url):
  result =  re.search("authors\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    result = re.search("authors\/([0-9|a-z|]{32})", url)
    if result is None:
      raise ParseError("Invalid author url")
  uuid_str = result.group(1)
  return str(uuid.UUID(uuid_str))


def get_comment_id_from_url(url):
  result = re.search("comments\/([0-9|a-z|]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12})", url)
  if result is None:
    result = re.search("comments\/([0-9|a-z|]{32})", url)
    if result is None:
      raise ParseError("Invalid comment url")
  uuid_str = result.group(1)
  return str(uuid.UUID(uuid_str))


def get_or_create_user(obj):
  if is_uuid(obj["id"]):
    id = obj["id"]
  else:
    id = get_author_id_from_url(obj["id"])
  if User.objects.filter(id=id).exists():
    return User.objects.get(id=id)
  else:
    user = User.objects.create(
      id=id,
      username=obj["displayName"] + str(uuid.uuid4()),
      displayName=obj["displayName"],
      email="default@email.com",
      password="default",
      host = obj["host"],
      url = obj["url"],
      github = obj.get("github", None),
      is_foreign = True,
      image_url = obj["profileImage"]
    )
    user.save()
    return user
  
  
def create_comment_from_request_data(request_data, post_obj):
  author = request_data.get('author', None)
  author_obj = get_or_create_user(author)
  comment = request_data.get('comment', None)
  published = request_data.get('published', None)
  id = request_data.get('id', None)
  if is_uuid(id):
    comment_id = id
  else:
    comment_id = get_comment_id_from_url(id)
  created_at = parse_time(published)
  
  if not Comment.objects.filter(id=comment_id).exists():
    comment_obj = Comment.objects.create(id=comment_id, post=post_obj, user=author_obj, content=comment, created_at=created_at)
  else:
    comment_obj = Comment.objects.get(id=comment_id)
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
  if is_uuid(id):
    post_id = id
  else:
    post_id = get_post_id_from_url(id)
  
  
  post_obj = None
  if Post.objects.filter(id=post_id).exists():
    post_obj = Post.objects.get(id=post_id)
    
    # don't update local post as we always have the latest version of the local post
    if post_obj.is_foreign:
      post_obj.title = title
      post_obj.source = source
      post_obj.origin = origin
      post_obj.contentType = contentType
      post_obj.content = content
      post_obj.visibility = visibility
      post_obj.unlisted = unlisted
      post_obj.created_at = parse_time(published)
      post_obj.save()
  
  else:
    author_obj = get_or_create_user(author)
    is_foreign = author_obj.is_foreign
    post_obj = Post.objects.create(id=post_id, title=title, source=source, origin=origin, content=content, contentType=contentType, author=author_obj, visibility=visibility, unlisted=unlisted, created_at=parse_time(published), is_foreign=is_foreign)
    post_obj.save()
  
  if not PostAccess.objects.filter(post=post_obj, user=receiver_obj).exists():
    PostAccess.objects.create(post=post_obj, user=receiver_obj)
  print("created post access")
    
  for comment in comments:
    create_comment_from_request_data(comment, post_obj)
  
  return post_obj


def has_access_to_post(post_obj, user_obj):
  if post_obj.visibility == "PUBLIC":
    return True
  elif post_obj.visibility == "PRIVATE" or post_obj.visibility == "FRIENDS":
    if PostAccess.objects.filter(post=post_obj, user=user_obj).exists():
      return True
    elif post_obj.author.id == user_obj.id:
      return True
 
  return False

