# request_modifier.py
import json

class HTTPRequest:
    def __init__(self, method, url, headers=None, body=None, cookies=None):
        self.method = method
        self.url = url
        self.headers = headers if headers is not None else {}
        self.body = body
        self.cookies = cookies if cookies is not None else {}

    def set_method(self, method):
        self.method = method

    def set_url(self, url):
        self.url = url

    def add_header(self, key, value):
        self.headers[key] = value

    def remove_header(self, key):
        if key in self.headers:
            del self.headers[key]

    def set_body(self, body):
        self.body = body

    def add_cookie(self, key, value):
        self.cookies[key] = value

    def remove_cookie(self, key):
        if key in self.cookies:
            del self.cookies[key]

    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "cookies": self.cookies,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        request_line = f"{self.method} {self.url} HTTP/1.1"
        headers = "\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        cookies = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        body = self.body if self.body else ""
        return f"{request_line}\n{headers}\n\nCookies: {cookies}\n\n{body}"
