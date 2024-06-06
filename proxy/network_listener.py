import socket
import threading

class NetworkListener:
    def __init__(self, port, logger):
        self.port = port
        self.logger = logger
        self.server_socket = None

    def handle_client(self, client_socket):
        self.logger.log("Client connected")
        request = client_socket.recv(1024)
        self.logger.log(f"Received: {request.decode()}")

        # AWS 서버에 연결
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("43.202.51.186", 80))
        remote_socket.send(request)

        # AWS 서버로부터 응답을 받아 클라이언트로 전송
        response = remote_socket.recv(4096)
        client_socket.send(response)

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
