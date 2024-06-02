import socket
import threading
import sys

class NetworkListener:
    def __init__(self, port, handler_factory, ssl_context=None, logger=None):
        self.port = port
        self.handler_factory = handler_factory
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
            else:
                print(f"[INFO] Listening on port {self.port}")
            while self.running:
                client_socket, addr = self.server.accept()
                if self.ssl_context:
                    client_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
                if self.logger:
                    self.logger.log(f"[INFO] Connection accepted from {addr}")
                else:
                    print(f"[INFO] Connection accepted from {addr}")
                handler_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                handler_thread.start()
        except Exception as e:
            if self.logger:
                self.logger.log(f"[ERROR] Error setting up server: {e}")
            else:
                print(f"[ERROR] Error setting up server: {e}")
        finally:
            if self.server:
                self.server.close()
                if self.logger:
                    self.logger.log("[INFO] Server closed")
                else:
                    print("[INFO] Server closed")
                    
    def handle_client(self, client_socket, addr):
        try:
            if self.logger:
                self.logger.log(f"[INFO] Handling client {addr}")
            else:
                print(f"[INFO] Handling client {addr}")
            
            # 핸들러 생성 함수를 사용하여 TrafficIntercept 인스턴스를 생성하고 클라이언트 요청을 처리
            handler = self.handler_factory(self.port)
            handler.handle_client(client_socket, addr)
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"[ERROR] Error handling client {addr}: {e}")
            else:
                print(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            client_socket.close()  # 클라이언트 소켓을 닫음
            if self.logger:
                self.logger.log(f"[INFO] Connection closed with {addr}")
            else:
                print(f"[INFO] Connection closed with {addr}")

    def stop_server(self):
        self.running = False
        if self.server:
            self.server.close()
            if self.logger:
                self.logger.log("[INFO] Server is shutting down")
            else:
                print("[INFO] Server is shutting down")
