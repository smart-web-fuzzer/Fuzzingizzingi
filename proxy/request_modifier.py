import mysql.connector
from mysql.connector import Error
import json
from urllib.parse import urlparse, parse_qs

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

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

class HTTPResponse:
    def __init__(self, status_line, headers=None, body=None):
        self.status_line = status_line
        self.headers = headers if headers is not None else {}
        self.body = body
        self.cookies = self.parse_cookies(self.headers.get("Set-Cookie", ""))

    def parse_cookies(self, cookie_str):
        cookies = {}
        if cookie_str:
            cookie_pairs = cookie_str.split(", ")
            for pair in cookie_pairs:
                parts = pair.split(";")[0].split("=", 1)
                if len(parts) == 2:
                    key, value = parts
                    cookies[key] = value
        return cookies

    def to_dict(self):
        return {
            "status_line": self.status_line,
            "headers": self.headers,
            "body": self.body,
            "cookies": self.cookies,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        headers = "\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        cookies = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        body = self.body if self.body else ""
        return f"{self.status_line}\n{headers}\n\nCookies: {cookies}\n\n{body}"

def save_packet(connection, request, response):
    cursor = connection.cursor()
    try:
        # Insert into requests table
        insert_request_query = """
        INSERT INTO requests (url, parameters, method, protocol_version, headers, cookies, response_body)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        request_values = (
            request.url,
            json.dumps(request.url_params),
            request.method,
            request.protocol_version,
            json.dumps(request.headers),
            json.dumps(request.cookies),
            response.body
        )
        cursor.execute(insert_request_query, request_values)
        connection.commit()
        print("Request and Response saved successfully.")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()

# Example usage:
connection = create_connection("your_host", "your_username", "your_password", "your_db_name")

# Assuming you have an HTTPRequest and HTTPResponse instance:
request = HTTPRequest(
    method="GET",
    url="http://example.com",
    headers={"User-Agent": "test-agent", "Cookie": "test_cookie=1"},
    body=None,
    cookies={"test_cookie": "1"},
    user_agent="test-agent",
    protocol_version="HTTP/1.1"
)

response = HTTPResponse(
    status_line="HTTP/1.1 200 OK",
    headers={"Content-Type": "text/html; charset=UTF-8", "Set-Cookie": "response_cookie=1"},
    body="<html>Response body</html>"
)

save_packet(connection, request, response)

def parse_http_response(raw_response):
    # 응답을 줄 단위로 나눕니다.
    lines = raw_response.split("\n")
    
    # 상태 줄과 헤더를 분리합니다.
    status_line = lines[0]
    headers = {}
    body = ""
    is_body = False
    
    for line in lines[1:]:
        if is_body:
            body += line + "\n"
        elif line == "":
            is_body = True
        else:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
    
    response = HTTPResponse(status_line, headers, body)
    return response

raw_response = """HTTP/1.1 200 OK
Date: Sun, 02 Jun 2024 07:37:33 GMT
Expires: -1
Cache-Control: private, max-age=0
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-9Xoh0yslWpco6d7p8JxQ1Q' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Content-Encoding: gzip
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Set-Cookie: 1P_JAR=2024-06-02-07; expires=Tue, 02-Jul-2024 07:37:33 GMT; path=/; domain=.google.com; Secure, AEC=AQTF6HxHTgR6_lpfDKIdT7OnjogUM9vu7kbT-CK1KvwJivdTkkk2U3Uo0A; expires=Fri, 29-Nov-2024 07:37:33 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, NID=514=xCsUPAKbvuxzZCSznvx6HnmoTDKFqWjrGLvgCm53BKJAXfPHs_AuHCwkcR-Ea4l00Kwmdy_--GMg7x0Z8lJX5HO1-Z2Ln-Xq3kXsHkZZ_gOmYEZ1iP5fNjs6TbL8RrMuNrEnzA8xsRDXsKS7uXAB1t5AY-SYbI64_Rvlwh98NDY; expires=Mon, 02-Dec-2024 07:37:33 GMT; path=/; domain=.google.com; HttpOnly
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
Transfer-Encoding: chunked

<!doctype html><html itemscope="" itemtype="http://schema.org/WebPage" lang="ko"><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"><meta content="/images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>Google</title></head><body><h1>Google</h1><p>Welcome to Google!</p></body></html>
"""

# 줄인 응답 패킷을 파싱
response = parse_http_response(raw_response)

# 데이터베이스에 저장
save_packet(connection, request, response)
