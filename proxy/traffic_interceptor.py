import os
import re
import ssl
import socket
import threading
import time
from subprocess import PIPE, Popen
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import argparse
import sys
import glob

class CustomThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc_type, exc_value = sys.exc_info()[:2]
        if exc_type not in [socket.error, ssl.SSLError]:
            super().handle_error(request, client_address)

class CustomProxyRequestHandler(BaseHTTPRequestHandler):
    thread_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.thread_local = threading.local()
        self.thread_local.connections = {}
        super().__init__(*args, **kwargs)

    def do_CONNECT(self):
        host, _ = self.path.split(":", 1)
        if self._is_intercept_enabled(host):
            self._handle_intercept()
        else:
            self._handle_relay()

    def _is_intercept_enabled(self, host):
        return (
            os.path.isfile(cli_args.ca_key) and
            os.path.isfile(cli_args.ca_cert) and
            os.path.isfile(cli_args.cert_key) and
            os.path.isdir(cli_args.cert_dir) and
            (cli_args.domain == "*" or cli_args.domain == host)
        )

    def _handle_intercept(self):
        hostname = self.path.split(":")[0]
        certpath = os.path.join(cli_args.cert_dir, f"{hostname}.pem")
        confpath = os.path.join(cli_args.cert_dir, f"{hostname}.conf")

        with self.thread_lock:
            if not os.path.isfile(certpath):
                category = "IP" if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else "DNS"
                self._create_certificate_config(confpath, category, hostname)
                self._generate_certificate(certpath, confpath, hostname)

        self._send_intercept_response(certpath)

    def _create_certificate_config(self, confpath, category, hostname):
        with open(confpath, "w") as f:
            f.write(f"subjectAltName={category}:{hostname}\nextendedKeyUsage=serverAuth\n")

    def _generate_certificate(self, certpath, confpath, hostname):
        epoch = str(int(time.time() * 1000))
        p1 = Popen(["openssl", "req", "-sha256", "-new", "-key", cli_args.cert_key, "-subj", f"/CN={hostname}", "-addext", f"subjectAltName=DNS:{hostname}"], stdout=PIPE)
        p2 = Popen(["openssl", "x509", "-req", "-sha256", "-days", "365", "-CA", cli_args.ca_cert, "-CAkey", cli_args.ca_key, "-set_serial", epoch, "-out", certpath, "-extfile", confpath], stdin=p1.stdout, stderr=PIPE)
        p2.communicate()

    def _send_intercept_response(self, certpath):
        self.send_response(200, "Connection Established")
        self.end_headers()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.verify_mode = ssl.CERT_NONE
        context.load_cert_chain(certpath, cli_args.cert_key)
        self.connection = context.wrap_socket(self.connection, server_side=True)
        self.rfile = self.connection.makefile("rb", self.rbufsize)
        self.wfile = self.connection.makefile("wb", self.wbufsize)
        self._relay_connection_data()

    def _relay_connection_data(self):
        self.close_connection = False
        while not self.close_connection:
            rlist, _, xlist = select.select([self.connection, self.rfile], [], [self.connection, self.rfile], self.timeout)
            if xlist or not rlist:
                break
            for r in rlist:
                other = self.wfile if r is self.rfile else self.connection
                data = r.recv(8192)
                if not data:
                    self.close_connection = True
                    break
                other.sendall(data)

class TrafficIntercept:
    def __init__(self, db_connection, logger):
        self.db_connection = db_connection
        self.logger = logger

    def handle_client(self, client_socket, addr):
        from request_modifier import save_packet

        try:
            self.logger.log(f"Client connected from {addr}")
            request = client_socket.recv(4096)
            self.logger.log(f"Received: {request.decode()}")

            # AWS 서버에 연결
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect(("13.209.63.65", 80))
            remote_socket.send(request)

            # AWS 서버로부터 응답을 받아 클라이언트로 전송
            response = remote_socket.recv(4096)
            client_socket.send(response)

            # 요청 및 응답 데이터를 save_packet 함수에 전달
            save_packet(self.db_connection, request.decode(), response.decode())

            remote_socket.close()
        except Exception as e:
            self.logger.log(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            self.logger.log(f"Connection closed with {addr}")

    def start_server(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-b", "--bind", default="localhost", help="Host to bind")
        parser.add_argument("-p", "--port", type=int, default=7777, help="Port to bind")
        parser.add_argument("-d", "--domain", default="*", help="Domain to intercept, if not set, intercept all.")
        parser.add_argument("--ca-key", default="./ca-key.pem", help="CA key file")
        parser.add_argument("--ca-cert", default="./ca-cert.pem", help="CA cert file")
        parser.add_argument("--cert-key", default="./cert-key.pem", help="site cert key file")
        parser.add_argument("--cert-dir", default="./certs", help="Site certs files")
        parser.add_argument("--make-certs", action="store_true", help="Create https intercept certs")

        global cli_args
        cli_args = parser.parse_args()

        if cli_args.make_certs:
            self.generate_certs()
            sys.exit(0)

        protocol = "HTTP/1.1"
        http.server.test(
            HandlerClass=CustomProxyRequestHandler,
            ServerClass=CustomThreadingHTTPServer,
            protocol=protocol,
            port=cli_args.port,
            bind=cli_args.bind,
        )

    def generate_certs(self):
        try:
            os.makedirs(cli_args.cert_dir, exist_ok=True)
            
            # Create CA key
            ca_key_command = ["openssl", "genrsa", "-out", cli_args.ca_key, "2048"]
            Popen(ca_key_command).communicate()
            self.logger.log("CA key generated")

            # Create CA certificate
            ca_cert_command = [
                "openssl", "req", "-new", "-x509", "-days", "3650", "-key", cli_args.ca_key,
                "-sha256", "-out", cli_args.ca_cert, "-subj", "/CN=Proxy3 CA"
            ]
            Popen(ca_cert_command).communicate()
            self.logger.log("CA certificate generated")

            # Create server key
            cert_key_command = ["openssl", "genrsa", "-out", cli_args.cert_key, "2048"]
            Popen(cert_key_command).communicate()
            self.logger.log("Server key generated")

            # Clean up old certificates
            for old_cert in glob.glob(os.path.join(cli_args.cert_dir, "*.pem")):
                os.remove(old_cert)
            self.logger.log("Old certificates removed")

        except Exception as e:
            self.logger.log(f"Error generating certificates: {e}")

if __name__ == "__main__":
    TrafficIntercept(None, None).start_server()
