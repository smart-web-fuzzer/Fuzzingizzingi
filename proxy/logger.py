from datetime import datetime
import json

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

class VulnerabilityReport:
    def __init__(self, url, vulnerability_type, payload, http_request, http_response, severity):
        self.url = url
        self.timestamp = datetime.now().isoformat()
        self.vulnerability_type = vulnerability_type
        self.severity = severity
        self.payload = payload
        self.http_request = http_request
        self.http_response = http_response

    def to_dict(self):
        return {
            "URL": self.url,
            "Timestamp": self.timestamp,
            "Vulnerability Type": self.vulnerability_type,
            "Severity": self.severity,
            "Payload": self.payload,
            "HTTP Request": self.http_request,
            "HTTP Response": self.http_response,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
