from .base_server_adapter import BaseServerAdapter
from .io_adapters.base_io_adapter import BaseIOAdapter

class IOAdapter(BaseIOAdapter):
    def outputTransformer(self, output):
        output = dict(output)
        for item in output["items"]:
            item['id'] = item['url']
        return output


class RestLessClientsAdapter(BaseServerAdapter):
    base_url = "https://restlessclients-7b4ebf6b9382.herokuapp.com/api/"
    host = "restlessclients-7b4ebf6b9382.herokuapp.com"
    username_env = "RESTLESS_CLIENTS_USERNAME"
    password_env = "RESTLESS_CLIENTS_PASSWORD"
