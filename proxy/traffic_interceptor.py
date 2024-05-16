import os
import sys
import socket
import argparse

# 커맨드로부터 포트번호 받기
parser = argparse.ArgumentParser()
parser.add_argument('-p', type=int, help="port number")
args = parser.parse_args()
my_port = args.p
if(my_port):
    pass
else:
    print("[!] python <file.py> -p <port> 형식으로 접속해주세요!")
    sys.exit()

# 터미널창 비우기 (Windows용, Linux/Mac에서는 'clear' 사용)
os.system('cls' if os.name == 'nt' else 'clear')
print("Proxy Started\n")

# Cache 사전
cache = {}
# HTTP 메소드 종류
http = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTION", "TRACE"]

# 사용자와 연결하기 위한 소켓 생성
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', my_port))
s.listen(10)  # 리슨
print(f">> [{my_port}] Listening...\n")
c, addr = s.accept()  # 연결
print(">> Connected!\n")

while True:
    req = c.recv(65535).decode()  # 요청 패킷 가져와서 디코딩

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
        info = info.encode()
        c.send(info)
        continue

    try:
        index = '/'.join(url.split("/")[3:])  # 파일경로
        root = url.split("/")[2]  # IP/도메인
    except:
        index = ''
        root = url

    if msg != "GET":  # GET이 아닌 경우
        if msg in http:
            info = "[!] Not Implemented(501)!\n"
        else:
            info = "[!] Bad Request(400)!\n"
        print(info)
        info = info.encode()
        c.send(info)
        print(">> Keep going...\n")
        continue
    else:  # GET인 경우
        print("* * * Request * * *\n")
        print(req + "\n")

        # root + index
        target = root + "/" + index

        # Cache가 있는 경우
        if target in cache:
            get = cache[target]
            get = get.replace("$$$", ":")
            get = get.replace("###", "{")
            get = get.replace("@@@", ",")
            get = get.encode()
            c.sendall(get)
            print(">> Cache Used!\n")
            continue

        # 절대경로 -> 상대경로
        new_req = f"GET /{index} HTTP/1.1\r\nHost: {root}\r\nConnection: close\r\n\r\n"
        new_req = new_req.encode()

        # 오리진 서버와 연결하기 위한 소켓 생성
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            host = socket.gethostbyname(f"{root}")
        except:
            info = "[!] There's no such Host!\n"
            print(info)
            info = info.encode()
            c.send(info)
            print(">> Keep going...\n")
            continue
        host_port = 80
        s2.connect((host, host_port))

        # 오리진 서버에 요청 패킷 전송
        s2.sendall(new_req)
        value = ""  # 응답 패킷 내용을 저장할 빈 문자열
        bad = False

        while True:
            res = s2.recv(65535)  # 응답 가져오기
            if not res:
                break
            # 응답 패킷을 Cache 사전에 저장하기 위해 디코딩
            deco = res.decode()
            deco = deco.replace(":", "$$$")
            deco = deco.replace("{", "###")
            deco = deco.replace(",", "@@@")
            value += deco  # 문자열에 패킷 내용 저장
            if deco.split()[1] == "400":
                info = "[!] Bad Request(400)!\n"
                print(info)
                info = info.encode()
                c.send(info)
                bad = True
                break
            # 응답 패킷을 사용자에게 전송
            c.sendall(res)
        print(">> Send Success!\n")

        if bad:
            print(">> Keep going...\n")
            continue

        # Cache 저장
        cache[target] = value
        print(">> New Cache Written!\n")
        print("* * * Cache List * * *")
        for index, key in enumerate(cache.keys()):
            print(f"[{index + 1}] {key}")
        print("\n>> Keep going...\n")
