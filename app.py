from flask import Flask, jsonify, request, render_template
from proxy.logger import Logger  # 수정된 logger 모듈 import

class PacketLoggerServer:
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.logger = Logger()  # Logger 인스턴스 생성
        self.setup_routes()
        self.add_sample_logs()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/logs')
        def logs():
            return render_template('logs.html')

        @self.app.route('/report')
        def report():
            return render_template('report.html')

        @self.app.route('/log_packet', methods=['POST'])
        def log_packet():
            data = request.json
            self.logger.add_packet_log(
                source_ip=data['source_ip'],
                destination_url=data['destination_url'],
                request_size=data['request_size'],
                response_size=data['response_size']
            )
            return jsonify({"status": "success"}), 201

        @self.app.route('/logs_data', methods=['GET'])
        def get_logs():
            return jsonify(self.logger.get_packet_logs())

        @self.app.route('/report_data', methods=['GET'])
        def get_report():
            # 임시 리포트 데이터 생성
            report = self.logger.create_vulnerability_report(
                url="http://example.com/vulnerable",
                vulnerability_type="SQL Injection",
                payload="' OR '1'='1",
                http_request="GET /vulnerable?input=' OR '1'='1 HTTP/1.1\nHost: example.com",
                http_response="HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html>...</html>",
                severity="High"
            )
            return report

    def add_sample_logs(self):
        # 테스트를 위한 샘플 로그 데이터 추가
        sample_logs = [
            {"source_ip": "192.168.1.1", "destination_url": "http://example.com/page1", "request_size": 512, "response_size": 1024},
            {"source_ip": "192.168.1.2", "destination_url": "http://example.com/page2", "request_size": 256, "response_size": 512},
            {"source_ip": "192.168.1.3", "destination_url": "http://example.com/page3", "request_size": 128, "response_size": 256},
        ]
        for log in sample_logs:
            self.logger.add_packet_log(**log)

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

if __name__ == '__main__':
    server = PacketLoggerServer()
    server.run()
