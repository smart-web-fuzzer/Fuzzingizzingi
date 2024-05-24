import os
import sys
import socket
import argparse

class TrafficIntercept:
    def __init__(self, port):
        self.port = port
        self.cache = {}
        self.http_methods = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTION", "TRACE"]
        self.server_socket = None

    def start(self):
        # 터미널창 비우기 (Windows용, Linux/Mac에서는 'clear' 사용)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Proxy Started\n")

        # 사용자와 연결하기 위한 소켓 생성
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(10)  # 리슨
        print(f">> [{self.port}] Listening...\n")
        client_socket, addr = self.server_socket.accept()  # 연결
        print(">> Connected!\n")

        while True:
            req = client_socket.recv(65535).decode()  # 요청 패킷 가져와서 디코딩

            # telnet에서 엔터쳤을 때 IndexError방지
            try:
                parts = req.split()
                if len(parts) == 1 and parts[0].startswith('http'):
                    msg = "GET"
                    url = parts[0]
                else:
                    msg = parts[0]  # 메소드
                    url = parts[1]  # url
            except:
                info = "[!] Send some Request!\n"
                client_socket.send(info.encode())
                continue

            try:
                index = '/'.join(url.split("/")[3:])  # 파일경로
                root = url.split("/")[2]  # IP/도메인
            except:
                index = ''
                root = url

            if msg != "GET":  # GET이 아닌 경우
                self.handle_non_get_requests(client_socket, msg)
                continue
            else:  # GET인 경우
                self.handle_get_request(client_socket, req, root, index)

    def handle_non_get_requests(self, client_socket, msg):
        if msg in self.http_methods:
            info = "[!] Not Implemented(501)!\n"
        else:
            info = "[!] Bad Request(400)!\n"
        print(info)
        client_socket.send(info.encode())
        print(">> Keep going...\n")

    def handle_get_request(self, client_socket, req, root, index):
        print("* * * Request * * *\n")
        print(req + "\n")

        target = root + "/" + index

        if target in self.cache:
            self.send_cached_response(client_socket, target)
            return

        new_req = f"GET /{index} HTTP/1.1\r\nHost: {root}\r\nConnection: close\r\n\r\n"
        new_req = new_req.encode()

        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            host = socket.gethostbyname(f"{root}")
        except:
            info = "[!] There's no such Host!\n"
            print(info)
            client_socket.send(info.encode())
            print(">> Keep going...\n")
            return

        host_port = 80
        s2.connect((host, host_port))
        s2.sendall(new_req)
        value = ""
        bad = False

        while True:
            res = s2.recv(65535)
            if not res:
                break
            deco = res.decode()
            deco = deco.replace(":", "$$$")
            deco = deco.replace("{", "###")
            deco = deco.replace(",", "@@@")
            value += deco
            if deco.split()[1] == "400":
                info = "[!] Bad Request(400)!\n"
                print(info)
                client_socket.send(info.encode())
                bad = True
                break
            client_socket.sendall(res)
        print(">> Send Success!\n")

        if bad:
            print(">> Keep going...\n")
            return

        self.cache[target] = value
        print(">> New Cache Written!\n")
        print("* * * Cache List * * *")
        for index, key in enumerate(self.cache.keys()):
            print(f"[{index + 1}] {key}")
        print("\n>> Keep going...\n")

    def send_cached_response(self, client_socket, target):
        get = self.cache[target]
        get = get.replace("$$$", ":")
        get = get.replace("###", "{")
        get = get.replace("@@@", ",")
        client_socket.sendall(get.encode())
        print(">> Cache Used!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, help="port number")
    args = parser.parse_args()
    my_port = args.p
    if my_port:
        server = ProxyServer(my_port)
        server.start()
    else:
        print("[!] python <file.py> -p <port> 형식으로 접속해주세요!")
        sys.exit()
