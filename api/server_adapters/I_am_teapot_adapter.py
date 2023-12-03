from .base_server_adapter import BaseServerAdapter
import requests
import logging

class IAmTeaPotAdapter(BaseServerAdapter):
  base_url = "https://im-a-teapot-41db2c906820.herokuapp.com/api/"
  host = "im-a-teapot-41db2c906820.herokuapp.com"
  username_env = "I_AM_TEAPOT_USERNAME"
  password_env = "I_AM_TEAPOT_PASSWORD"
  
  def get_author_detail_url(self, author_id):
    return super().get_author_detail_url(author_id)
  
  def get_author_inbox_url(self, author_id):
    return super().get_author_inbox_url(author_id) + '/'
  
  