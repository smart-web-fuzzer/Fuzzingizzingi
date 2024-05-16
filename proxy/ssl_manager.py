import ssl
import socket

class SSLServer:
    def __init__(self, certfile, keyfile, host, port, context):
        self.certfile = certfile
        self.keyfile = keyfile
        self.host = host
        self.port = port
        self.context = self.ssl_context()
    
    # SSL 컨텍스트 생성
    def ssl_context(self):
        # 컨텍스트 생성 중 버전 설정
        # Cipher Suite
    
    # 클라이언트
    def handle_client(self):
        # 네트워크 통신 중 에러처리
        
    # 실행
    def run(self):
        # 세션 관리(타임아웃 설정)
    
# if __name__ == '__main__':