# proxy/logger.py

from datetime import datetime

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

class PacketLogStore:
    def __init__(self):
        self.logs = []

    def add_log(self, packet_log):
        self.logs.append(packet_log)

    def get_logs(self):
        return [log.to_dict() for log in self.logs]
