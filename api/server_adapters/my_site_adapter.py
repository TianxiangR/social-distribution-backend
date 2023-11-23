from .base_server_adapter import BaseServerAdapter

class MySiteAdapter(BaseServerAdapter):
  base_url = "https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/"
  host = "cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com"
  username_env = "MYSITE_USERNAME"
  password_env = "MYSITE_PASSWORD"