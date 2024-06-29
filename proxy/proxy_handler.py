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
from savepacket import save_packet_to_db  # 추가된 부분

class CustomProxyRequestHandler(BaseHTTPRequestHandler):
    lock = threading.Lock()

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
                        # 패킷 데이터 저장 (매번 저장하지 않고 요청 완료 후 저장하도록 수정)
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

    # 패킷 데이터 저장 (요청 완료 후 바로 저장)
    packet = {
        'url': request.path,
        'parameters': urllib.parse.parse_qs(parsed_url.query),
        'method': request.command,
        'protocol_version': request.request_version,
        'headers': dict(request.headers),
        'cookies': dict(urllib.parse.parse_qsl(request.headers.get('Cookie', ''))),
        'response_body': response_body_plain.decode('iso-8859-1')
    }
    save_packet_to_db([packet])

# 종료 시 패킷 데이터 저장 (더 이상 필요 없음)
# import atexit

# def save_packets():
#     save_packet_to_db(CustomProxyRequestHandler.packet_storage)

# atexit.register(save_packets)

                                            
