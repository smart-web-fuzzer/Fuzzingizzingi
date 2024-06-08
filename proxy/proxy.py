import sys
import signal
import socket
import threading
from network_listener import NetworkListener
from logger import Logger
from request_modifier import save_packet, create_connection

def signal_handler(server):
    def handler(signal, frame):
        print('Signal received, stopping server.')
        server.stop_server()
        sys.exit(0)
    return handler

class ProxyServer:
    def __init__(self, port, logger):
        self.port = port
        self.logger = logger
        self.server_socket = None
        self.db_connection = create_connection('localhost', 'zzingzzingi', '!Ru7eP@ssw0rD!12', 'fuzzingzzingi')

    def handle_client(self, client_socket):
        self.logger.log("Client connected")
        request_data = client_socket.recv(4096)
        self.logger.log(f"Received request: {request_data.decode()}")

        # 원격 서버에 연결
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("13.209.63.65", 80))
        remote_socket.send(request_data)

        # 원격 서버로부터 응답을 받아 클라이언트로 전송
        response_data = remote_socket.recv(4096)
        self.logger.log(f"Received response: {response_data.decode()}")
        client_socket.send(response_data)

        # 요청 및 응답 데이터를 save_packet 함수에 전달
        save_packet(self.db_connection, request_data.decode(), response_data.decode())

        remote_socket.close()
        client_socket.close()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(5)
        self.logger.log(f"Listening on port {self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            self.logger.log(f"Accepted connection from {addr}")
            handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            handler.start()

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()

if __name__ == "__main__":
    logger = Logger()
    logger.log("Starting the server...")

    port = 8888
    server = ProxyServer(port=port, logger=logger)
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(server)(s, f))
    
    try:
        server.start_server()
    except Exception as e:
        logger.log("Server encountered an error and stopped.")
        logger.log(str(e))
