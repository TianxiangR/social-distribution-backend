from .base_server_adapter import BaseServerAdapter
from .io_adapters.base_io_adapter import BaseIOAdapter

class IOAdapter(BaseIOAdapter):
    def outputTransformer(self, output):
        output = dict(output)
        for item in output:
            if item.get("contentType") is not None and "image" in item["contentType"]:
                # This is because RESTLessClients doesn't specify the content type for the image post as application/base64 :(
                # so we have to do the transformation here
                item["contentType"] = "application/base64"


class RestLessClientsAdapter(BaseServerAdapter):
    base_url = "https://restlessclients-7b4ebf6b9382.herokuapp.com/api/"
    host = "restlessclients-7b4ebf6b9382.herokuapp.com"
    username_env = "RESTLESS_CLIENTS_USERNAME"
    password_env = "RESTLESS_CLIENTS_PASSWORD"
    
    get_author_posts_request_adapter = IOAdapter()
    
    
