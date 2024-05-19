# server.py

from flask import Flask, jsonify, request, render_template
from proxy.logger import PacketLogStore, PacketLog

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
            report_data = {
                "total_requests": len(self.log_store.get_logs()),
                "summary": "This is a summary of the packet log data."
            }
            return jsonify(report_data)

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)
