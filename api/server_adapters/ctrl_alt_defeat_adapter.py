from .base_server_adapter import BaseServerAdapter

class CtrlAltDefeatAdapter(BaseServerAdapter):
  base_url = "https://ctrl-alt-defeat-2.herokuapp.com/"
  host = "ctrl-alt-defeat-2.herokuapp.com"
  username_env = "CTRL_ALT_DEFEAT_USERNAME"
  password_env = "CTRL_ALT_DEFEAT_PASSWORD"