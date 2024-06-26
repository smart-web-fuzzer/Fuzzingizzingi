import json
from urllib.parse import urlparse, parse_qs
from mysql.connector import Error

class HTTPRequest:
    def __init__(self, raw_data):
        self.method = None
        self.url = None
        self.headers = {}
        self.body = None
        self.cookies = {}
        self.user_agent = None
        self.protocol_version = "HTTP/1.1"

        self.raw_data = raw_data
        self.parse_request(raw_data)

    def parse_request(self, raw_data):
        lines = raw_data.split("\r\n")
        request_line = lines[0]
        self.method, self.url, self.protocol_version = request_line.split(" ")
        header_lines = lines[1:]
        self.headers = self.parse_headers(header_lines)

    def parse_headers(self, header_lines):
        headers = {}
        for line in header_lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
                if key == "Cookie":
                    self.cookies = self.parse_cookies(value)
                if key == "User-Agent":
                    self.user_agent = value
        return headers

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
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class HTTPResponse:
    def __init__(self, raw_data):
        self.status_line = None
        self.headers = {}
        self.body = None
        self.cookies = {}

        self.raw_data = raw_data
        self.parse_response(raw_data)

    def parse_response(self, raw_data):
        lines = raw_data.split("\r\n")
        self.status_line = lines[0]
        header_lines = lines[1:]
        self.headers = self.parse_headers(header_lines)
        if "\r\n\r\n" in raw_data:
            self.body = raw_data.split("\r\n\r\n", 1)[1]

    def parse_headers(self, header_lines):
        headers = {}
        for line in header_lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
                if key == "Set-Cookie":
                    self.cookies = self.parse_cookies(value)
        return headers

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

def save_packet(connection, raw_request, raw_response):
    if connection is None:
        print("Database connection failed.")
        return

    cursor = connection.cursor()
    try:
        request = HTTPRequest(raw_request)
        response = HTTPResponse(raw_response)

        # requests 테이블에 데이터 추가
        insert_request_query = """
        INSERT INTO requests (url, method, protocol_version, headers, cookies, request_body)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        request_values = (
            request.url,
            request.method,
            request.protocol_version,
            json.dumps(request.headers),
            json.dumps(request.cookies),
            request.body
        )
        cursor.execute(insert_request_query, request_values)
        connection.commit()

        # responses 테이블에 데이터 추가
        insert_response_query = """
        INSERT INTO responses (status_line, headers, body)
        VALUES (%s, %s, %s)
        """
        response_values = (
            response.status_line,
            json.dumps(response.headers),
            response.body
        )
        cursor.execute(insert_response_query, response_values)
        connection.commit()

        print("Request and Response saved successfully.")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()