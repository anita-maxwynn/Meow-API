## 🐾 MeowAPI – A Minimalist Web Framework with Catitude!

MeowAPI is a lightweight, WSGI-compatible Python web framework inspired by the simplicity of Flask — with a cute cat theme! 😺
It supports function-based routes, class-based views, middleware, and automatic route logging into SQLite.

---

### 📦 Features

* 🧶 WSGI-based: Pure Python, no dependencies except `Jinja2` for templates.
* 🐾 Function-based & class-based routing.
* 🧩 Global & per-route middleware support.
* 📓 Auto-persisted routes using SQLite.
* 🐱 Cute emoji-based logging.
* 📄 Simple JSON and HTML response helpers.
* 🎨 Optional Jinja2 templating support.
* 🐈 Default cat-themed homepage.

---

## 🚀 Getting Started

### 1. 🔧 Installation

```bash
git clone https://github.com/your-username/meowapi.git
cd meowapi
pip install -r requirements.txt
```

> **Required package:**

```bash
pip install jinja2
```

---

### 2. 🐍 Running the Server (Dev Style)

You can run your app like this:

```python
# serve.py
from wsgiref.simple_server import make_server
from main import MeowAPI
from response import Response

app = MeowAPI()

@app.get("/bruh")
def index(environ, start_response):
    return Response("yo mama fat")(start_response)

def start_server():
    with make_server('', 8000, app) as httpd:
        print("🐱 MeowAPI server is running at http://localhost:8000 ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server shut down gracefully. Meow~ 🐾")

if __name__ == "__main__":
    start_server()
```

Now run it:

```bash
python serve.py
```

---

## 🧪 Usage Guide

### ✅ Function-based Routes

```python
@app.get("/hello")
def say_hello(environ, start_response):
    return Response("Hello MeowAPI!")(start_response)
```

Also supports:

```python
@app.post("/submit")
@app.put("/update")
@app.delete("/remove")
```

---

### ✅ Class-based Views

```python
@app.view("/cats")
class CatView:
    def get(self, environ, start_response):
        return Response("List of cats")(start_response)

    def post(self, environ, start_response):
        return Response("Create a new cat")(start_response)
```

---

### ✅ Dynamic URL Parameters

```python
@app.get("/cat/{name}")
def show_cat(environ, start_response):
    name = MeowAPI.get_route_params(environ).get("name", "unknown")
    return Response(f"Hello, {name} 🐱")(start_response)
```

---

### ✅ Middleware Support

Global middleware (for all routes):

```python
def global_middleware(environ, start_response):
    print("🐾 Global middleware activated!")
    return None

app = MeowAPI(middleware=[global_middleware])
```

Per-route middleware:

```python
@app.get("/secure", middleware=[my_auth_middleware])
def secure_endpoint(environ, start_response):
    ...
```

---

## 🖼️ Jinja2 Templating

Place your HTML files in a `templates/` folder. For example:

**templates/default.html**

```html
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
  <h1>{{ title }}</h1>
  <p>{{ message }}</p>
</body>
</html>
```

Render using:

```python
return Response("").render("default", {"title": "Meow", "message": "Nya~"})
```

---

## 🐾 Built-in Logs

Logs automatically look like:

```
🐾🐱 [INFO] New route registered: GET /hello → say_hello
🐾 Route called: GET /hello → 200 OK
🚫 Route not found: GET /invalid → 404 Not Found
💥 Exception in route: POST /crash → 500 Internal Server Error
```

---

## 🔐 Routes Stored in SQLite

Each route is saved in a `routes.db` file. If you modify a route, it gets **updated** automatically.

---

## 🔧 ASGI Support?

Not yet, but it’s being planned. For now, MeowAPI uses WSGI and works great with:

* `wsgiref.simple_server` (dev)
* `gunicorn` (prod):

```bash
gunicorn serve:app
```

---

## 🧹 Clean Shutdown

When using `serve.py`, pressing `Ctrl+C` exits cleanly:

```
👋 Server shut down gracefully. Meow~ 🐾
```

---

## ❤️ Inspired by

* Flask (Python)
* Cat memes 😸
* Rivaan Ranawat ([https://github.com/RivaanRanawat](https://github.com/RivaanRanawat))

---

## 📁 Project Structure (Typical)

```
meowapi/
├── main.py
├── response.py
├── serve.py
├── templates/
│   └── default.html
├── static/
    └── favicon.iso
├── routes.db
└── README.md
```

---

## 🌟 Explore More Examples

Want to see MeowAPI in action? Check out **`example.py`** for a collection of ready-to-run code samples covering:

- Function-based and class-based routes
- Middleware usage
- Dynamic URL parameters
- Jinja2 templating
- Error handling and more!

Just open `example.py`, run, and start experimenting. Happy coding! 🐾✨

