# serve.py
from wsgiref.simple_server import make_server
from response import Response
from main import MeowAPI

app=MeowAPI()

@app.get("/bruh")
def index(environ, start_response):
    return Response('yo mama fat')(start_response)



def start_server():
    with make_server('', 8000, app) as httpd:
        print("🐱 MeowAPI server is running at http://localhost:8000 ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server shut down gracefully. Meow~ 🐾")

if __name__ == "__main__":
    start_server()

