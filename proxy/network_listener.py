import socket
import threading
import sys

class NetworkListener:
    def __init__(self, port, ssl_context=None, logger=None):
        self.port = port
        self.ssl_context = ssl_context  # SSL 컨텍스트 저장
        self.logger = logger  # logger 인스턴스 저장
        self.server = None
        self.running = True

    def start_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('localhost', self.port))
            self.server.listen(5)
            if self.logger:
                self.logger.log(f"[INFO] Listening on port {self.port}")
            while self.running:
                client_socket, addr = self.server.accept()
                if self.logger:
                    self.logger.log(f"[INFO] Connection accepted from {addr}")
                handler_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                handler_thread.start()
        except Exception as e:
            if self.logger:
                self.logger.log(f"[ERROR] Error setting up server: {e}")
        finally:
            if self.server:
                self.server.close()
                if self.logger:
                    self.logger.log("[INFO] Server closed")
                    
    def handle_client(self, client_socket, addr):
        try:
            if self.logger:
                self.logger.log(f"[INFO] Handling client {addr}")
            while True:
                data = client_socket.recv(1024)  # 데이터를 1024 바이트 단위로 수신
                if not data:
                    break  # 연결이 종료되었으면 루프 종료
                if self.logger:
                    self.logger.log(f"[INFO] Received data from {addr}: {data.decode()}")
                response = f"Echo: {data.decode()}"  # 수신된 데이터에 간단한 에코 응답
                client_socket.sendall(response.encode())  # 응답 전송
        except Exception as e:
            if self.logger:
                self.logger.log(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            client_socket.close()  # 클라이언트 소켓을 닫음
            if self.logger:
                self.logger.log(f"[INFO] Connection closed with {addr}")
        # 클라이언트로부터 받은 데이터가 없어서 바로 소켓을 닫도록 되어있음
        # 코드 수정 필요

    def stop_server(self):
        self.running = False
        if self.server:
            self.server.close()
            if self.logger:
                self.logger.log("[INFO] Server is shutting down")