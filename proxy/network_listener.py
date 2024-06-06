import socket
import threading

class NetworkListener:
    def handle_client(client_socket):
        print("Client connected")  # 클라이언트가 접속했음을 출력
        request = client_socket.recv(1024)
        print(f"Received: {request.decode()}")

        # AWS 서버에 연결
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("43.202.51.186", 80))
        remote_socket.send(request)

        # AWS 서버로부터 응답을 받아 클라이언트로 전송
        response = remote_socket.recv(4096)
        client_socket.send(response)

        remote_socket.close()
        client_socket.close()

    def start_proxy_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 8888))
        server.listen(5)
        print("Listening on port 8888")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            handler = threading.Thread(target=handle_client, args=(client_socket,))
            handler.start()

if __name__ == "__main__":
    start_proxy_server()
