import os
import sys
import socket
import argparse
import select

class TrafficIntercept:
    def __init__(self, port):
        self.port = port
        self.cache = {}
        self.http_methods = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTIONS", "TRACE", "CONNECT"]
        self.server_socket = None

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Proxy Started\n")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(10)
        print(f">> [{self.port}] Listening...\n")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(">> Connected!\n")
            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        req = client_socket.recv(65535).decode()

        try:
            parts = req.split()
            if len(parts) == 1 and parts[0].startswith('http'):
                msg = "GET"
                url = parts[0]
            else:
                msg = parts[0]
                url = parts[1]
        except:
            info = "[!] Send some Request!\n"
            client_socket.send(info.encode())
            client_socket.close()
            return

        if msg == "CONNECT":
            self.handle_connect_request(client_socket, url)
        elif msg != "GET":
            self.handle_non_get_requests(client_socket, msg)
        else:
            self.handle_get_request(client_socket, req, url)

    def handle_connect_request(self, client_socket, url):
        try:
            server_socket = socket.create_connection((url.split(":")[0], int(url.split(":")[1])))
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            sockets = [client_socket, server_socket]
            while True:
                readable, _, _ = select.select(sockets, [], [])
                for s in readable:
                    data = s.recv(65535)
                    if not data:
                        break
                    if s is client_socket:
                        server_socket.sendall(data)
                    else:
                        client_socket.sendall(data)
        except Exception as e:
            print(f"[!] Error handling CONNECT request: {e}")
        finally:
            client_socket.close()
            server_socket.close()

    def handle_non_get_requests(self, client_socket, msg):
        if msg in self.http_methods:
            info = "[!] Not Implemented(501)!\n"
        else:
            info = "[!] Bad Request(400)!\n"
        print(info)
        client_socket.send(info.encode())
        print(">> Keep going...\n")
        client_socket.close()

    def handle_get_request(self, client_socket, req, url):
        print("* * * Request * * *\n")
        print(req + "\n")

        try:
            index = '/'.join(url.split("/")[3:])
            root = url.split("/")[2]
        except:
            index = ''
            root = url

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
            client_socket.close()
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
        client_socket.close()
        s2.close()

    def send_cached_response(self, client_socket, target):
        get = self.cache[target]
        get = get.replace("$$$", ":")
        get = get.replace("###", "{")
        get = get.replace("@@@", ",")
        client_socket.sendall(get.encode())
        print(">> Cache Used!\n")
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, help="port number")
    args = parser.parse_args()
    my_port = args.p
    if my_port:
        server = TrafficIntercept(my_port)
        server.start()
    else:
        print("[!] python <file.py> -p <port> 형식으로 접속해주세요!")
        sys.exit()
