import json
from urllib.parse import urlparse, parse_qs

class HTTPRequest:
    def __init__(self, method, url, headers=None, body=None, cookies=None, user_agent=None, protocol_version="HTTP/1.1"):
        self.method = method
        self.url = url
        self.headers = headers if headers is not None else {}
        self.body = body
        self.cookies = cookies if cookies is not None else {}
        self.user_agent = user_agent
        self.protocol_version = protocol_version

        self.url_params = self.parse_url_params(url)
        self.cookie_dict = self.parse_cookies(self.headers.get("Cookie", ""))

    def set_method(self, method):
        self.method = method

    def set_url(self, url):
        self.url = url
        self.url_params = self.parse_url_params(url)

    def add_header(self, key, value):
        self.headers[key] = value

    def remove_header(self, key):
        if key in self.headers:
            del self.headers[key]

    def set_body(self, body):
        self.body = body

    def add_cookie(self, key, value):
        self.cookies[key] = value
        self.update_cookie_header()

    def remove_cookie(self, key):
        if key in self.cookies:
            del self.cookies[key]
            self.update_cookie_header()

    def set_user_agent(self, user_agent):
        self.user_agent = user_agent
        self.headers["User-Agent"] = user_agent

    def set_protocol_version(self, protocol_version):
        self.protocol_version = protocol_version

    def parse_url_params(self, url):
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)

    def parse_cookies(self, cookie_str):
        cookies = {}
        if cookie_str:
            cookie_pairs = cookie_str.split("; ")
            for pair in cookie_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    cookies[key] = value
        return cookies

    def update_cookie_header(self):
        self.headers["Cookie"] = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])

    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "cookies": self.cookies,
            "user_agent": self.user_agent,
            "protocol_version": self.protocol_version,
            "url_params": self.url_params,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        request_line = f"{self.method} {self.url} {self.protocol_version}"
        headers = "\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        cookies = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        body = self.body if self.body else ""
        return f"{request_line}\n{headers}\n\nCookies: {cookies}\n\n{body}"

# 이 코드는 사용 예시 코드이며 수정필요 
if __name__ == "__main__":
    request = HTTPRequest(
        method="GET",
        url="http://example.com?param1=value1&param2=value2",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cookie": "sessionId=abc123; userId=789",
        },
        body=None,
        user_agent="Mozilla/5.0",
        protocol_version="HTTP/1.1"
    )
    print(request.to_json())
    print("URL Params:", request.url_params)
    print("Cookies:", request.cookie_dict)
