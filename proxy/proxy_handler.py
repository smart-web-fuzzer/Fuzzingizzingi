import os
import re
import socket
import ssl
import time
import urllib.parse
import http.client
import json
import threading
import logging
import select
from http.server import BaseHTTPRequestHandler
from utils import decode_content_body, encode_content_body, filter_headers, with_color
from savepacket import save_packet_to_db

class CustomProxyRequestHandler(BaseHTTPRequestHandler):
    lock = threading.Lock()
    packet_storage = []  # 패킷 저장을 위한 클래스 변수

    def __init__(self, *args, server_args=None, **kwargs):
        self.tls = threading.local()
        self.tls.conns = {}
        self.server_args = server_args
        super().__init__(*args, **kwargs)

    def log_error(self, format, *args):
        if isinstance(args[0], socket.timeout):
            logging.warning("Socket timeout occurred")
        else:
            logging.error(format % args)

    def do_CONNECT(self):
        handle_connect(self)

    def do_GET(self):
        handle_get(self)

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

    def connect_intercept(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        certfile = os.path.join(current_dir, 'certs', 'ca-cert.pem')
        keyfile = os.path.join(current_dir, 'certs', 'cert-key.pem')

        logging.debug(f"Using certfile: {certfile}")
        logging.debug(f"Using keyfile: {keyfile}")
        logging.debug(f"Current working directory: {current_dir}")

        if not os.path.exists(certfile) or not os.path.exists(keyfile):
            logging.error(f"Certificate files not found. Certfile: {certfile}, Keyfile: {keyfile}")
            self.send_error(500, "Certificate files not found")
            return

        self.send_response(200, "Connection Established")
        self.end_headers()
        conns = [self.connection, None]

        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # TLS 1.2 이상만 허용
            conns[1] = context.wrap_socket(conns[0], server_side=True)
        except FileNotFoundError as e:
            logging.error(f"SSL certificate or key file not found: {str(e)}")
            self.send_error(500, f"SSL certificate or key file not found: {str(e)}")
            return
        except ssl.SSLError as e:
            logging.error(f"SSL error: {str(e)}")
            self.send_error(500, f"SSL error: {str(e)}")
            return
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            self.send_error(500, f"Unexpected error: {str(e)}")
            return

        self._read_write(conns)

    def connect_relay(self):
        host, port = self.path.split(":", 1)
        port = int(port)
        remote_socket = socket.create_connection((host, port))
        self.send_response(200, "Connection Established")
        self.end_headers()
        conns = [self.connection, remote_socket]
        self._read_write(conns)

    def _read_write(self, conns):
        try:
            while True:
                r, w, e = select.select(conns, [], conns, 10)
                if e:
                    break
                if r:
                    for s in r:
                        data = s.recv(8192)
                        if not data:
                            return
                        if s is conns[0]:
                            conns[1].sendall(data)
                        else:
                            conns[0].sendall(data)
                        # 패킷 데이터 저장
                        CustomProxyRequestHandler.packet_storage.append(data)
                        # 일정 주기마다 패킷 저장
                        if len(CustomProxyRequestHandler.packet_storage) > 100:
                            save_packet_to_db(CustomProxyRequestHandler.packet_storage)
                            CustomProxyRequestHandler.packet_storage.clear()
        except Exception as e:
            logging.error(f"Error in _read_write: {str(e)}")

    def relay_streaming(self, response):
        self.send_response_only(response.status, response.reason)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        try:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                # 패킷 데이터 저장
                CustomProxyRequestHandler.packet_storage.append(chunk)
                # 일정 주기마다 패킷 저장
                if len(CustomProxyRequestHandler.packet_storage) > 100:
                    save_packet_to_db(CustomProxyRequestHandler.packet_storage)
                    CustomProxyRequestHandler.packet_storage.clear()
            self.wfile.flush()
        except socket.error:
            pass

def handle_connect(proxy_handler):
    host, _ = proxy_handler.path.split(":", 1)
    if (os.path.isfile(proxy_handler.server.args.ca_key)
        and os.path.isfile(proxy_handler.server.args.ca_cert)
        and os.path.isfile(proxy_handler.server.args.cert_key)
        and os.path.isdir(proxy_handler.server.args.cert_dir)
        and (proxy_handler.server.args.domain == "*" or proxy_handler.server.args.domain == host)):
        proxy_handler.connect_intercept()
    else:
        proxy_handler.connect_relay()

def handle_get(proxy_handler):
    request = proxy_handler
    content_length = int(request.headers.get("Content-Length", 0))
    request_body = proxy_handler.rfile.read(content_length) if content_length else b""

    if request.path[0] == "/":
        if isinstance(proxy_handler.connection, ssl.SSLSocket):
            request.path = "https://%s%s" % (request.headers["Host"], request.path)
        else:
            request.path = "http://%s%s" % (request.headers["Host"], request.path)

    parsed_url = urllib.parse.urlsplit(request.path)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path + "?" + parsed_url.query if parsed_url.query else parsed_url.path
    assert scheme in ("http", "https")
    if netloc:
        request.headers["Host"] = netloc
    request.headers = filter_headers(request.headers)

    origin = (scheme, netloc)
    try:
        if origin not in proxy_handler.tls.conns:
            if scheme == "https":
                proxy_handler.tls.conns[origin] = http.client.HTTPSConnection(
                    netloc, timeout=proxy_handler.timeout
                )
            else:
                proxy_handler.tls.conns[origin] = http.client.HTTPConnection(
                    netloc, timeout=proxy_handler.timeout
                )
        connection = proxy_handler.tls.conns[origin]
        connection.request(proxy_handler.command, path, request_body, dict(request.headers))
        response = connection.getresponse()

        cache_control = response.headers.get("Cache-Control", "")
        if "Content-Length" not in response.headers and "no-store" in cache_control:
            response.headers = filter_headers(response.headers)
            proxy_handler.relay_streaming(response)
            return

        response_body = response.read()
    except Exception:
        if origin in proxy_handler.tls.conns:
            del proxy_handler.tls.conns[origin]
        proxy_handler.send_error(502)
        return

    response_body_plain = decode_content_body(response_body, response.headers.get("Content-Encoding", "identity"))
    response_body = encode_content_body(response_body_plain, response.headers.get("Content-Encoding", "identity"))
    response.headers["Content-Length"] = str(len(response_body))

    response.headers = filter_headers(response.headers)

    proxy_handler.send_response_only(response.status, response.reason)
    for key, value in response.headers.items():
        proxy_handler.send_header(key, value)
    proxy_handler.end_headers()
    proxy_handler.wfile.write(response_body)
    proxy_handler.wfile.flush()

    # 패킷 데이터 저장
    CustomProxyRequestHandler.packet_storage.append(request_body)
    CustomProxyRequestHandler.packet_storage.append(response_body_plain)
    # 일정 주기마다 패킷 저장
    if len(CustomProxyRequestHandler.packet_storage) > 100:
        save_packet_to_db(CustomProxyRequestHandler.packet_storage)
        CustomProxyRequestHandler.packet_storage.clear()

    # 추가된 로그 출력
    display_info(request, request_body, response, response_body_plain)

def relay_streaming(proxy_handler, response):
    proxy_handler.send_response_only(response.status, response.reason)
    for key, value in response.headers.items():
        proxy_handler.send_header(key, value)
    proxy_handler.end_headers()
    try:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            proxy_handler.wfile.write(chunk)
            # 패킷 데이터 저장
            CustomProxyRequestHandler.packet_storage.append(chunk)
            # 일정 주기마다 패킷 저장
            if len(CustomProxyRequestHandler.packet_storage) > 100:
                save_packet_to_db(CustomProxyRequestHandler.packet_storage)
                CustomProxyRequestHandler.packet_storage.clear()
        proxy_handler.wfile.flush()
    except socket.error:
        pass

def display_info(request, request_body, response, response_body):
    request_header_text = "%s %s %s\n%s" % (
        request.command,
        request.path,
        request.request_version,
        request.headers,
    )
    version_table = {10: "HTTP/1.0", 11: "HTTP/1.1"}
    response_header_text = "%s %d %s\n%s" % (
        version_table[response.version],
        response.status,
        response.reason,
        response.headers,
    )

    print(with_color(33, request_header_text))

    parsed_url = urllib.parse.urlsplit(request.path)
    if parsed_url.query:
        query_text = urllib.parse.parse_qsl(parsed_url.query)
        print(with_color(32, "==== QUERY PARAMETERS ====\n%s\n" % query_text))

    cookie_header = request.headers.get("Cookie", "")
    if cookie_header:
        cookie_header = urllib.parse.parse_qsl(re.sub(r";\s*", "&", cookie_header))
        print(with_color(32, "==== COOKIE ====\n%s\n" % cookie_header))

    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("basic"):
        token = authorization.split()[1].decode("base64")
        print(with_color(31, "==== BASIC AUTH ====\n%s\n" % token))

    if request_body:
        request_body_text = None
        content_type = request.headers.get("Content-Type", "")

        if content_type.startswith("application/x-www-form-urlencoded"):
            request_body_text = urllib.parse.parse_qsl(request_body)
        elif content_type.startswith("application/json"):
            try:
                json_obj = json.loads(request_body)
                json_str = json.dumps(json_obj, indent=2)
                if json_str.count("\n") < 50:
                    request_body_text = json_str
                else:
                    lines = json_str.splitlines()
                    request_body_text = "%s\n(%d lines)" % (
                        "\n".join(lines[:50]), 
                        len(lines),
                    )
            except ValueError:
                request_body_text = request_body
        elif len(request_body) < 1024:
            request_body_text = request_body

        if request_body_text:
            print(with_color(32, "==== REQUEST BODY ====\n%s\n" % request_body_text))

    print(with_color(36, response_header_text))

    cookies = response.headers.get("Set-Cookie")
    if cookies:
        print(with_color(31, "==== SET-COOKIE ====\n%s\n" % cookies))

    if response_body:
        response_body_text = None
        content_type = response.headers.get("Content-Type", "")

        if content_type.startswith("application/json"):
            try:
                json_obj = json.loads(response_body)
                json_str = json.dumps(json_obj, indent=2)
                if json_str.count("\n") < 50:
                    response_body_text = json_str
                else:
                    lines = json_str.splitlines()
                    response_body_text = "%s\n(%d lines)" % (
                        "\n".join(lines[:50]),
                        len(lines),
                    )
            except ValueError:
                response_body_text = response_body
        elif content_type.startswith("text/html"):
            match = re.search(rb"<title[^>]*>\s*([^<]+?)\s*</title>", response_body, re.I)
            if match:
                print(
                    with_color(
                        32, "==== HTML TITLE ====\n%s\n" % match.group(1).decode()
                    )
                )
        elif content_type.startswith("text/") and len(response_body) < 1024:
            response_body_text = response_body

        if response_body_text:
            print(with_color(32, "==== RESPONSE BODY ====\n%s\n" % response_body_text))
