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
  
  # def request_get_author_list(self):
  #   url = self.get_author_list_url()
  #   response = requests.get(url, auth=(self.username, self.password))
  #   print("IAmTeaPotAdapter: request_get_author_list: response: ", response)
  #   return {
  #     "status_code": response.status_code,
  #     "body": response.json() if response.status_code == 200 else []
  #   }
  
  