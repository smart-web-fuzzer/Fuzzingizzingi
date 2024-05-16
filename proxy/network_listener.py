import socket
import threading
import signal
import sys

class NetworkListener:
    def __init__(self, port):
        # 생성자: 포트 번호 초기화, 서버 소켓 변수 선언, 실행 상태 표시
        self.port = port
        self.server = None
        self.running = True

    def start_server(self):
        # 서버 시작 메소드
        try:
            # 소켓 생성 및 설정
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('0.0.0.0', self.port)) 
            self.server.listen(5)  
            print(f"[INFO] Listening on port {self.port}")

            # 서버 실행 루프
            while self.running:
                try:
                    # 클라이언트 연결 수락
                    client_socket, addr = self.server.accept()
                    if client_socket:
                        print(f"[INFO] Connection accepted from {addr}")
                        # 연결된 클라이언트를 처리하기 위한 새 스레드 시작
                        handler_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                        handler_thread.start()
                except Exception as e:
                    # 연결 수락 중 예외 발생 처리
                    if self.running:
                        print(f"[ERROR] Error accepting client connection: {e}")
                    else:
                        print("[INFO] Server shutting down")

        except Exception as e:
            # 서버 설정 중 예외 발생 처리
            print(f"[ERROR] Error setting up server: {e}")
        finally:
            # 서버 소켓 종료
            if self.server:
                self.server.close()
                print("[INFO] Server closed")

    def stop_server(self):
        # 서버 종료 메소드
        self.running = False
        self.server.close()

def signal_handler(signal, frame):
    print('Signal received, stopping server.')
    server.stop_server()

if __name__ == "__main__":
    # 메인 실행 부
    server = NetworkListener(8888) 
    signal.signal(signal.SIGINT, signal_handler) 
    server.start_server()  
