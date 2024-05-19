# server.py

from flask import Flask, jsonify, request, render_template
from proxy.logger import PacketLogStore, PacketLog, VulnerabilityReport

class PacketLoggerServer:
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.log_store = PacketLogStore()
        self.setup_routes()

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
            packet_log = PacketLog(
                source_ip=data['source_ip'],
                destination_url=data['destination_url'],
                request_size=data['request_size'],
                response_size=data['response_size']
            )
            self.log_store.add_log(packet_log)
            return jsonify({"status": "success"}), 201

        @self.app.route('/logs_data', methods=['GET'])
        def get_logs():
            return jsonify(self.log_store.get_logs())

        @self.app.route('/report_data', methods=['GET'])
        def get_report():
            # 임시 리포트 데이터 생성
            report = VulnerabilityReport(
                url="http://example.com/vulnerable",
                vulnerability_type="SQL Injection",
                payload="' OR '1'='1",
                http_request="GET /vulnerable?input=' OR '1'='1 HTTP/1.1\nHost: example.com",
                http_response="HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html>...</html>",
                severity="High",
                description="입력값이 제대로 검증되지 않아 SQL 쿼리가 조작될 수 있음.",
                impact="데이터베이스 조작 가능, 민감 정보 유출 위험",
                reproduction_steps="1. 웹 브라우저에서 URL에 페이로드를 포함하여 접속합니다.\n2. 서버 응답을 확인하여 민감 데이터가 노출되는지 확인합니다.",
                recommendation="입력값 검증 및 필터링, 준비된 쿼리 사용, ORM 사용하여 쿼리 생성"
            )
            return report.to_json()

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)
