import socket
import ssl
import sys
import threading
import logging
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from proxy_handler import CustomProxyRequestHandler

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET  # IPv4를 사용하도록 명시적으로 설정
    daemon_threads = True

    def handle_error(self, request, client_address):
        exception_class, exception_instance = sys.exc_info()[:2]
        if exception_class in [socket.error, ssl.SSLError]:
            logging.error(f"Socket or SSL error: {exception_instance}")
        else:
            logging.error(f"Unexpected error: {exception_instance}")
            super().handle_error(request, client_address)