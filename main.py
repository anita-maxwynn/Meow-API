import sqlite3
import os
import traceback
from typing import Callable, Any
from response import Response
from parse import parse

class MeowAPI:
    def __init__(self, middleware=None, db_path="routes.db"):
        self.routes = {}
        self.middleware = middleware or []
        self.db_path = db_path
        self._init_db()
        self._set_default_root_handler()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                method TEXT,
                path TEXT,
                handler_name TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _upsert_route(self, method, path, handler):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM routes WHERE method = ? AND path = ?', (method, path))
        exists = cursor.fetchone()[0]

        if exists:
            cursor.execute('''
                UPDATE routes SET handler_name = ? WHERE method = ? AND path = ?
            ''', (handler.__name__, method, path))
            self._log(f"🐾 Route updated: {method} {path} → {handler.__name__}")
        else:
            cursor.execute('''
                INSERT INTO routes (method, path, handler_name)
                VALUES (?, ?, ?)
            ''', (method, path, handler.__name__))
            self._log(f"🐾 New route registered: {method} {path} → {handler.__name__}")

        conn.commit()
        conn.close()

    def _log(self, message, error=False):
        if error:
            print(f"🐾😿 [ERROR] {message}")
        else:
            print(f"🐾🐱 [INFO] {message}")

    def _set_default_root_handler(self):
        def default_root_handler(environ, start_response):
            return Response(
                body="Kore Nya!🐱 MeowAPI is running!",
                status='200 OK',
                content_type='text/plain'
            ).render("default")(start_response)
        self.routes[('GET', '/')] = [default_root_handler, []]
        self._upsert_route('GET', '/', default_root_handler)

    def _apply_middlewares(self, middleware_list, environ, start_response):
        for middleware in middleware_list:
            if callable(middleware):
                response = middleware(environ, start_response)
                if response is not None:
                    return response
        return None

    def register_handler(self, method: str, path: str, handler: Callable, middleware: list = None):
        key = (method.upper(), path)
        self.routes[key] = [handler, middleware or []]
        self._upsert_route(method.upper(), path, handler)

    def register_class_view(self, path: str, view_class: type, middleware: list = None):
        methods = ['GET', 'POST', 'PUT', 'DELETE']

        for method in methods:
            if hasattr(view_class, method.lower()):
                handler_method = getattr(view_class(), method.lower())
                if not callable(handler_method):
                    continue

                def make_handler(func, method=method, path=path):
                    def handler(environ, start_response):
                        return func(environ, start_response)
                    return handler

                wrapped_handler = make_handler(handler_method)
                wrapped_handler.__name__ = f"{view_class.__name__}.{method.lower()}"
                self.register_handler(method, path, wrapped_handler, middleware)

    def __call__(self, environ, start_response) -> Any:
        try:
            response = self._apply_middlewares(self.middleware, environ, start_response)
            if response:
                return response

            path = environ.get('PATH_INFO', '/')
            method = environ.get('REQUEST_METHOD', 'GET').upper()

            route_info = self.routes.get((method, path))
            if route_info:
                handler, local_middlewares = route_info
                response = self._apply_middlewares(local_middlewares, environ, start_response)
                if response:
                    return response
                self._log(f"🐾 Route called: {method} {path} → 200 OK")
                return handler(environ, start_response)

            for (route_method, route_path), (handler, local_middlewares) in self.routes.items():
                if route_method == method:
                    match = parse(route_path, path)
                    if match is not None:
                        environ['route_params'] = match.named
                        response = self._apply_middlewares(local_middlewares, environ, start_response)
                        if response:
                            return response
                        self._log(f"🐾 Route matched: {method} {path} → {route_path} → 200 OK")
                        return handler(environ, start_response)

            # Handle static files
            if method == 'GET' and path.startswith('/static/'):
                return self._serve_static_file(path, start_response)

            self._log(f"🚫 Route not found: {method} {path} → 404 Not Found", error=True)
            return Response(
                body="404: Not Found",
                status='404 Not Found',
                content_type='text/plain'
            )(start_response)
        except Exception:
            path = environ.get('PATH_INFO', '/')
            method = environ.get('REQUEST_METHOD', 'GET').upper()
            self._log(f"💥 Exception in route: {method} {path} → 500 Internal Server Error", error=True)
            traceback.print_exc()
            return Response(
                body="500: Internal Server Error",
                status='500 Internal Server Error',
                content_type='text/plain'
            )(start_response)

    def get(self, path=None, middleware=None):
        return self._method_decorator('GET', path, middleware)

    def post(self, path=None, middleware=None):
        return self._method_decorator('POST', path, middleware)

    def put(self, path=None, middleware=None):
        return self._method_decorator('PUT', path, middleware)

    def delete(self, path=None, middleware=None):
        return self._method_decorator('DELETE', path, middleware)

    def _method_decorator(self, method: str, path: str, middleware: list = None):
        def wrapper(handler):
            route_path = path or f"/{handler.__name__}"

            def wrapped_handler(environ, start_response):
                return handler(environ, start_response)

            wrapped_handler.__name__ = handler.__name__
            wrapped_handler.__doc__ = handler.__doc__
            wrapped_handler.__module__ = handler.__module__

            self.register_handler(method, route_path, wrapped_handler, middleware)
            return wrapped_handler

        return wrapper

    def view(self, path: str, middleware: list = None):
        def decorator(cls):
            self.register_class_view(path, cls, middleware)
            return cls
        return decorator

    def response(self, body, status='200 OK', content_type='text/plain'):
        return Response(body, status, content_type)

    def json_response(self, data, status='200 OK'):
        return Response("", status).json(data)

    @staticmethod
    def get_route_params(environ):
        return environ.get('route_params', {})

    def _serve_static_file(self, path, start_response):
        """Serve static files from the static directory"""
        try:
            # Remove /static/ prefix and get the file path
            file_path = path[8:]  # Remove '/static/'
            static_file_path = os.path.join('static', file_path)
            
            # Security check: prevent directory traversal
            if '..' in file_path or file_path.startswith('/'):
                self._log(f"🚫 Blocked unsafe static file access: {path}", error=True)
                return Response(
                    body="403: Forbidden",
                    status='403 Forbidden',
                    content_type='text/plain'
                )(start_response)
            
            # Check if file exists
            if not os.path.exists(static_file_path):
                self._log(f"🚫 Static file not found: {static_file_path}", error=True)
                return Response(
                    body="404: File Not Found",
                    status='404 Not Found',
                    content_type='text/plain'
                )(start_response)
            
            # Determine content type based on file extension
            content_type = self._get_content_type(file_path)
            
            # Read and serve the file
            with open(static_file_path, 'rb') as f:
                file_content = f.read()
            
            self._log(f"📁 Static file served: {path} → {content_type}")
            return Response(
                body=file_content,
                status='200 OK',
                content_type=content_type
            )(start_response)
            
        except Exception as e:
            self._log(f"💥 Error serving static file {path}: {e}", error=True)
            return Response(
                body="500: Internal Server Error",
                status='500 Internal Server Error',
                content_type='text/plain'
            )(start_response)

    def _get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.ico': 'image/x-icon',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.txt': 'text/plain',
            '.json': 'application/json'
        }
        return content_types.get(ext, 'application/octet-stream')
