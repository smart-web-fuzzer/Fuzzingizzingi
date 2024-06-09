# class file_download:
#
#     def __init__(self, ):

import socket
import time
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.crawler import MySpider
from proxy.certificate_manager import create_certificate, update_nginx_config
# from Myproject.Myproject.items import PacketFromDB
# from Myproject.Myproject.spiders.go_to_fuzzer import SendToFuzzer
# from server import PacketLoggerServer

def connect_server():
    try:
        server_ip = "13.209.63.65"
        server_port = 8888
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        client_socket.connect((server_ip, server_port))
        print("연결 성공")
        client_socket.close()
    except Exception as e:
        print("Failed to connect to server:", e)

def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def main():
    print("======================================================================")
    print('''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⢀⣠⣤⣶⠾⠟⠛⠛⠛⠛⠛⠛⠻⠷⣶⣤⣄⡀⠀⠀⠀⠀⠀
    ⠀⠀⠀⣠⡾⠟⠋⠁⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠈⠙⠻⢷⣄⠀⠀⠀
    ⠀⢀⣾⠋⠀⠀⠀⠀⠶⠶⠿⠛⠛⠛⠛⠛⠛⠿⠶⠶⠀⠀⠀⠀⠙⣷⡀⠀
    ⠀⣿⠃⠀⠀⠀⠀⠀⢀⣠⣤⣤⡀⠀⠀⢀⣤⣤⣄⡀⠀⠀⠀⠀⠀⠘⣿⠀
    ⠘⣿⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣧⣼⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⣿⠃
    ⠀⠻⣧⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⣼⠟⠀
    ⠀⠀⠙⢷⣄⡀⠘⣿⠛⠛⣿⡟⠛⢻⡟⠛⢻⣿⠛⠛⣿⠁⢀⣠⡾⠋⠀⠀
    ⠀⠀⠀⠀⠉⠻⢷⣿⣧⠀⠉⠁⣠⡿⢿⣄⠈⠉⠀⣼⣿⡾⠟⠉⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢹⣷⣶⣾⡟⠀⠀⢻⣷⣶⣾⡏⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⣀⣀⣸⣿⢀⣿⠁⠀⠀⠈⣿⡀⣿⣇⣀⣀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⣴⡟⠋⢉⣉⣀⣸⡏⠀⠀⠀⠀⢹⣇⣀⣉⡉⠙⢻⣦⠀⠀⠀⠀
    ⠀⠀⠀⠀⣿⡀⠘⠛⠛⠉⣹⣷⠀⠀⠀⠀⣾⣏⠉⠛⠛⠃⢀⣿⠀⠀⠀⠀
    ⠀⠀⠀⠀⠘⠻⠷⠾⠛⠛⠛⠛⢷⣤⣤⡾⠛⠛⠛⠛⠷⠾⠟⠃⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀
    ''')

    print("Hello, this is Fuzzingzzingi")
    print("This fuzzer is a program developed together by WHS 2nd class trainees.")
    print("======================================================================\n")
    time.sleep(0.7)

    connect_server()

    # URL 입력 받기
    print("Please enter the target URL")
    target_url = input("> ")
    
    # 도메인 추출
    domain = extract_domain(target_url)

    # 인증서 생성 및 Nginx 설정 업데이트
    key_file, crt_file = create_certificate(domain)
    update_nginx_config(domain, key_file, crt_file)

    # Scrapy 크롤러 프로세스 시작
    process = CrawlerProcess(get_project_settings())
    process.crawl(MySpider, start_url=domain)  # MySpider 클래스의 이름을 사용
    process.start()

    # 옵션 선택... 토글 방식으로 ON/OFF 구현........
    print("======================================================================")
    print("Select option")
    print("1. XSS")
    print("2. SQL Injection")
    print("3. SSRF")
    print("4. Command Injection")
    print("5. File Upload Vulnerabilities")
    print("6. File Download Vulnerabilities")
    print("7. ALL")
    print("======================================================================")

    # 선택한 취약점에 따른 코드 실행 구현 import 해서 구현하면 될듯

    # 이거 DB -> 크롤러 받은 패킷 fuzzer로 보내는 건데 아직 미완성이라 주석 처리 할게요~
    # SendToFuzzer.send()

    # 보고서 기능 구현

    # 오류 처리 기능 및 로깅 기능 구현


if __name__ == '__main__':
    main()
    # server = PacketLoggerServer()
    # server.run()