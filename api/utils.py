from .models import User, Post
from rest_framework.generics import get_object_or_404
from django.http import HttpResponseBadRequest
import uuid
from urllib3.util import parse_url

def clip_id_from_url(url):
  tokens = url.split('/')
  if len(tokens) == 0:
    return '-1'
  return tokens[-1]


def get_or_create_foreign_user(obj):
  id = clip_id_from_url(obj["id"])
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
  

def is_comment_url(url):
  parse_result = parse_url(url)
  path = parse_result.path
  tokens = path.split('/')

  