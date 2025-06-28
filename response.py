import re
import json
from jinja2 import Environment, FileSystemLoader
class Response:
    def __init__(self, body, status='200 OK', content_type='text/plain'):
        self.body = body.encode() if isinstance(body, str) else body
        self.status = status
        self.headers = [('Content-Type', content_type)]

    def __call__(self, start_response):
        start_response(self.status, self.headers)
        return [self.body]

    def json(self, data):
        self.body = json.dumps(data).encode()
        self._set_content_type('application/json')
        return self

    def render(self, template, context=None):
        env = Environment(loader=FileSystemLoader('templates'))
        template_obj = env.get_template(f"{template}.html")
        rendered = template_obj.render(context or {})
        self.body = rendered.encode()
        self.headers[0] = ('Content-Type', 'text/html')
        self.status = '200 OK'
        return self

    