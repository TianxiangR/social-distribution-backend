from .base_server_adapter import BaseServerAdapter

class CtrlAltDefeatAdapter(BaseServerAdapter):
  base_url = "https://cmput404-ctrl-alt-defeat-api-12dfa609f364.herokuapp.com/api/"
  host = "cmput404-ctrl-alt-defeat-api-12dfa609f364.herokuapp.com"
  username_env = "CTRL_ALT_DEFEAT_USERNAME"
  password_env = "CTRL_ALT_DEFEAT_PASSWORD"