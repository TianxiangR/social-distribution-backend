from .base_server_adapter import BaseServerAdapter

class IAmTeaPotAdapter(BaseServerAdapter):
  base_url = "https://cmput-average-21-b54788720538.herokuapp.com/api/"
  host = "cmput-average-21-b54788720538.herokuapp.com"
  username_env = "I_AM_TEAPOT_USERNAME"
  password_env = "I_AM_TEAPOT_PASSWORD"
  
  