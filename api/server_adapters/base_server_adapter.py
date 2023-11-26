import requests
from .io_adapters.base_io_adapter import BaseIOAdapter
import os
import json
import logging

class BaseServerAdapter():
  host = None
  base_url = None
  username_env = None
  password_env = None
  get_author_list_request_adapter = BaseIOAdapter()
  get_author_detail_request_adapter = BaseIOAdapter()
  get_author_followers_request_adapter = BaseIOAdapter()
  get_author_following_check_request_adapter = BaseIOAdapter()
  get_author_posts_request_adapter = BaseIOAdapter()
  get_author_post_detail_request_adapter = BaseIOAdapter()
  get_author_image_post_request_adapter = BaseIOAdapter()
  get_author_post_comments_request_adapter = BaseIOAdapter()
  get_author_post_comment_detail_request_adapter = BaseIOAdapter()
  get_author_post_likes_request_adapter = BaseIOAdapter()
  get_author_post_comment_likes_request_adapter = BaseIOAdapter()
  get_author_liked_request_adapter = BaseIOAdapter()
  get_author_inbox_request_adapter = BaseIOAdapter()
  post_author_post_comment_request_adapter = BaseIOAdapter()
  post_author_post_like_request_adapter = BaseIOAdapter()
  post_author_post_comment_like_request_adapter = BaseIOAdapter()
  post_author_inbox_request_adapter = BaseIOAdapter()
  post_detail_request_adapter = BaseIOAdapter()
  
  def __init__(self):
    self.password = os.environ.get(self.password_env)
    self.username = os.environ.get(self.username_env)
   
  def get_author_list_url(self):
    return self.base_url + 'authors/'
    
  def get_author_detail_url(self, author_id):
    return self.base_url + 'authors/' + str(author_id) + '/'
    
  def get_author_followers_url(self, author_id):
    return self.base_url + 'authors/' + str(author_id) + '/followers'
    
  def get_author_following_check_url(self, author_id, target_author_id):
    return self.base_url + 'authors/' + str(author_id) + '/followers/' + str(target_author_id)
    
  def get_author_posts_url(self, author_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/'
    
  def get_author_post_detail_url(self, author_id, post_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/' + str(post_id)
  
  def get_author_image_post_url(self, author_id, post_id):
    return self.base_url + 'author/' + str(author_id) + '/posts/' + str(post_id) + '/image'
  
  def get_author_post_comments_url(self, author_id, post_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/' + str(post_id) + '/comments'
  
  def get_author_post_comment_detail_url(self, author_id, post_id, comment_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/' + str(post_id) + '/comments/' + str(comment_id)
  
  def get_author_post_likes_url(self, author_id, post_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/' + str(post_id) + '/likes'
  
  def get_author_post_comment_likes_url(self, author_id, post_id, comment_id):
    return self.base_url + 'authors/' + str(author_id) + '/posts/' + str(post_id) + '/comments/' + str(comment_id) + '/likes'
  
  def get_author_liked_url(self, author_id):
    return self.base_url + 'authors/' + str(author_id) + '/liked'
  
  def get_author_inbox_url(self, author_id):
    return self.base_url + 'authors/' + str(author_id) + '/inbox'
  
  def get_post_detail_url(self, post_id):
    return self.base_url + 'posts/' + str(post_id)
  
  def request_get_author_list(self):
    url = self.get_author_list_url()
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    if resp.status_code > 299:
      logging.error(resp.content)
      print(url)
    
    try:
      resp_data = self.get_author_list_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data.get('items', [])
    except json.decoder.JSONDecodeError:
      response['body'] = []
    return response
  
  def request_get_author_detail(self, author_id):
    url = self.get_author_detail_url(author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    try:
      resp_data = self.get_author_detail_request_adapter.outputTransformer(resp.json())
    except json.decoder.JSONDecodeError:
      resp_data = None
    response['body'] = resp_data
    return response
  
  def request_get_author_followers(self, author_id):
    url = self.get_author_followers_url(author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    try:
      resp_data = self.get_author_followers_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data
    except json.decoder.JSONDecodeError:
      response['body'] = []
    return response
  
  def request_get_author_following_check(self, author_id, target_author_id):
    url = self.get_author_following_check_url(author_id, target_author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    try:
      resp_data = self.get_author_following_check_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data
    except json.decoder.JSONDecodeError:
      response['body'] = {}
    return response
  
  def request_get_author_posts(self, author_id):
    url = self.get_author_posts_url(author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    try:
      resp_data = self.get_author_posts_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data.get('items', [])
    except json.decoder.JSONDecodeError:
      response['body'] = []
    return response
  
  def request_get_author_post_detail(self, author_id, post_id):
    url = self.get_author_post_detail_url(author_id, post_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    try: 
      resp_data = self.get_author_post_detail_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data
    except json.decoder.JSONDecodeError:
      response['body'] = {}
    return response
  
  def request_get_author_image_post(self, author_id, post_id):
    url = self.get_author_image_post_url(author_id, post_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    response['body'] = resp.content
    return response
  
  def request_get_author_post_comments(self, author_id, post_id):
    url = self.get_author_post_comments_url(author_id, post_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    resp_data = self.get_author_post_comments_request_adapter.outputTransformer(resp.json())
    response['body'] = resp_data
    return response
  
  def request_get_author_post_comment_detail(self, author_id, post_id, comment_id):
    url = self.get_author_post_comment_detail_url(author_id, post_id, comment_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    resp_data = self.get_author_post_comment_detail_request_adapter.outputTransformer(resp.json())
    response['body'] = resp_data
    return response
  
  def request_get_author_post_likes(self, author_id, post_id):
    url = self.get_author_post_likes_url(author_id, post_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    resp_data = self.get_author_post_likes_request_adapter.outputTransformer(resp.json())
    response['body'] = resp_data
    return response
  
  def request_get_author_post_comment_likes(self, author_id, post_id, comment_id):
    url = self.get_author_post_comment_likes_url(author_id, post_id, comment_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    resp_data = self.get_author_post_comment_likes_request_adapter.outputTransformer(resp.json())
    response['body'] = resp_data
    return response
  
  def request_get_author_liked(self, author_id):
    url = self.get_author_liked_url(author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    response['body'] = self.get_author_liked_request_adapter.outputTransformer(resp.json())
    return response
  
  def request_get_author_inbox(self, author_id):
    url = self.get_author_inbox_url(author_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    
    resp_data = self.get_author_inbox_request_adapter.outputTransformer(resp.json())
    response['body'] = resp_data
    return response
  
  def request_post_author_inbox(self, author_id, data):
    url = self.get_author_inbox_url(author_id)
    request_data = self.post_author_inbox_request_adapter.inputTransformer(data)
    resp = requests.post(url, json=request_data, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    return response
  
  def request_post_author_post_comment(self, author_id, post_id, data):
    url = self.get_author_post_comments_url(author_id, post_id)
    request_data = self.get_author_post_comments_request_adapter.inputTransformer(data)
    resp = requests.post(url, json=request_data, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    return response
  
  def request_post_author_post_like(self, author_id, post_id, data):
    url = self.get_author_inbox_url(author_id)
    resp = requests.post(url, auth=(self.username, self.password), json=data)
    response = {}
    response['status_code'] = resp.status_code
    return response
  
  def request_post_author_post_comment_like(self, author_id, post_id, comment_id, data):
    url = self.get_author_inbox_url(author_id)
    resp = requests.post(url, auth=(self.username, self.password), json=data)
    response = {}
    response['status_code'] = resp.status_code
    return response
  
  def request_post_detail(self, post_id):
    url = self.get_post_detail_url(post_id)
    resp = requests.get(url, auth=(self.username, self.password))
    response = {}
    response['status_code'] = resp.status_code
    response['body'] = None
    try:
      resp_data = self.post_detail_request_adapter.outputTransformer(resp.json())
      response['body'] = resp_data
    except json.decoder.JSONDecodeError:
      pass
      
    return response
