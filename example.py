from response import Response
from main import MeowAPI

# Define middleware first
def global_middleware(environ, start_response):
    print("Global middleware processing request")
    return None  # Let the request proceed to actual handler


def local_middleware(environ, start_response):
    print("Local middleware processing request")
    return None  # Let the request proceed to actual handler

slice = MeowAPI()


@slice.view("/example",middleware=[global_middleware])
class ExampleView:
    def __init__(self):
        self.message = "Hello from ExampleView!"

    def get(self, environ, start_response):
        print("GET request handled by ExampleView")
        return Response(self.message)(start_response)
    def post(self, environ, start_response):
        print("POST request handled by ExampleView")
        return Response("POST request received in ExampleView!")(start_response)
    def put(self, environ, start_response):
        print("PUT request handled by ExampleView")
        return Response("PUT request processed in ExampleView!")(start_response)
    def delete(self, environ, start_response):
        print("DELETE request handled by ExampleView")
        return Response("DELETE request processed in ExampleView!")(start_response)


@slice.get("/hello",middleware=[local_middleware])
def hello_get(environ, start_response):
    return Response('GET Hello from MeowAPI!')(start_response)

@slice.post("/hello",)
def hello_post(environ, start_response):
    return Response('POST Hello received!')(start_response)

@slice.put("/hello")
def hello_put(environ, start_response):
    return Response('PUT Hello update!')(start_response)

@slice.delete("/hello")
def hello_delete(environ, start_response):
    return Response('DELETE Hello removed!')(start_response)

@slice.get("/json-example")
def json_example(environ, start_response):
    data = {"message": "Hello from JSON!", "status": "success"}
    return Response("").json(data)(start_response)

@slice.get("/meow/{id}")
def meow(environ, start_response):
    route_params = environ.get('route_params', {})
    meow_id = route_params.get('id', 'unknown')
    data = {
        "message": "Kore Nya!🐱 MeowAPI is running!",
        "meow_id": meow_id,
        "status": "success"
    }
    return Response("").json(data)(start_response)

@slice.get("/users/{user_id}/posts/{post_id}")
def get_user_post(environ, start_response):
    route_params = environ.get('route_params', {})
    user_id = route_params.get('user_id', 'unknown')
    post_id = route_params.get('post_id', 'unknown')
    data = {
        "user_id": user_id,
        "post_id": post_id,
        "message": f"Fetching post {post_id} for user {user_id}"
    }
    return Response("").json(data)(start_response)


@slice.get("/")
def index(environ, start_response):
    context = {
        "title": "Welcome to MeowAPI",
        "description": "This is a simple example of a web API using MeowAPI framework."
    }
    return Response("").render(template="example",context=context )(start_response)






if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    port = 8000
    print(f"🐾 MeowAPI is running on http://localhost:{port} 🐱")
    with make_server("", port, slice) as server:
        server.serve_forever()