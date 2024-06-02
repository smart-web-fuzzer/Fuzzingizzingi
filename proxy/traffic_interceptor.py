import os
import sys
import socket
import ssl
import argparse
import select
import threading
import signal
import requests
from network_listener import NetworkListener  # 동일 폴더에 있는 NetworkListener를 임포트

class TrafficIntercept:
    def __init__(self, port):
        self.port = port
        self.cache = {}
        self.http_methods = ["GET"]
        self.server_socket = None

    def handle_client(self, client_socket, addr):
        try:
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
        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            print(f"[INFO] Connection closed with {addr}")

    def handle_connect_request(self, client_socket, url):
        try:
            target_host, target_port = url.split(":")
            target_port = int(target_port)
            with socket.create_connection((target_host, target_port)) as server_socket:
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

        try:
            response = requests.get(url)
            # 응답 헤더와 본문을 클라이언트로 전송
            headers = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
            headers += ''.join([f"{k}: {v}\r\n" for k, v in response.headers.items()])
            headers += "\r\n"
            client_socket.sendall(headers.encode() + response.content)

            # 캐시에 저장
            self.cache[target] = headers + response.text
            print(">> New Cache Written!\n")
            print("* * * Cache List * * *")
            for index, key in enumerate(self.cache.keys()):
                print(f"[{index + 1}] {key}")
            print("\n>> Keep going...\n")
        except requests.RequestException as e:
            info = f"[!] Error fetching URL {url}: {e}\n"
            print(info)
            client_socket.send(info.encode())
        finally:
            client_socket.close()

    def send_cached_response(self, client_socket, target):
        get = self.cache[target]
        client_socket.sendall(get.encode())
        print(">> Cache Used!\n")
        client_socket.close()

def signal_handler(signal, frame):
    print('Signal received, stopping server.')
    server.stop_server()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, default=8888, help="port number (default: 8888)")
    args = parser.parse_args()
    my_port = args.p
    server = NetworkListener(my_port, handler_factory=TrafficIntercept)
    signal.signal(signal.SIGINT, signal_handler)
    server.start_server()
