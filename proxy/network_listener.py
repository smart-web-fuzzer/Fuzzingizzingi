import socket
import threading

class NetworkListener:
    def __init__(self, port, logger, db_connection, request_handler=None):
        self.port = port
        self.logger = logger
        self.server_socket = None
        self.request_handler = request_handler if request_handler else self.handle_client
        self.db_connection = db_connection

    def set_request_handler(self, handler):
        self.request_handler = handler

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
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(5)
            self.logger.log(f"Listening on port {self.port}")

            while True:
                client_socket, addr = self.server_socket.accept()
                self.logger.log(f"Accepted connection from {addr}")
                handler = threading.Thread(target=self.request_handler, args=(client_socket, addr))
                handler.start()
        except Exception as e:
            self.logger.log(f"[ERROR] Error starting server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                self.logger.log("Server socket closed")

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()