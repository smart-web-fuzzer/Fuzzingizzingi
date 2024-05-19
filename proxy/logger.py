# logger.py

from flask import Flask, jsonify, request
from datetime import datetime

# PacketLog 클래스 정의
class PacketLog:
    def __init__(self, source_ip, destination_url, request_size, response_size):
        self.timestamp = datetime.now()
        self.source_ip = source_ip
        self.destination_url = destination_url
        self.request_size = request_size
        self.response_size = response_size

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "destination_url": self.destination_url,
            "request_size": self.request_size,
            "response_size": self.response_size,
        }

# PacketLogStore 클래스 정의 (로그 저장소)
class PacketLogStore:
    def __init__(self):
        self.logs = []

    def add_log(self, packet_log):
        self.logs.append(packet_log)

    def get_logs(self):
        return [log.to_dict() for log in self.logs]

# Flask 웹 서버 설정
app = Flask(__name__)
log_store = PacketLogStore()

@app.route('/', methods=['GET'])
def index():
    return '''
    <h1>Packet Logger Service</h1>
    <a href="/log_packet">Log Packet</a>
    '''

@app.route('/log_packet', methods=['GET','POST'])
def log_packet():
    data = request.json
    packet_log = PacketLog(
        source_ip=data['source_ip'],
        destination_url=data['destination_url'],
        request_size=data['request_size'],
        response_size=data['response_size']
    )
    log_store.add_log(packet_log)
    return jsonify({"status": "success"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
