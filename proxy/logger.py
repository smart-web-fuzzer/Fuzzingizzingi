from datetime import datetime
import json

class Logger:
    def __init__(self):
        self.packet_logs = []
        
    def log(self, message):
        print(f"[LOG] {message}")  # 로그 메시지를 콘솔에 출력

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

    def add_packet_log(self, source_ip, destination_url, request_size, response_size):
        packet_log = self.PacketLog(source_ip, destination_url, request_size, response_size)
        self.packet_logs.append(packet_log)

    def get_packet_logs(self):
        return [log.to_dict() for log in self.packet_logs]

    def create_vulnerability_report(self, url, vulnerability_type, payload, http_request, http_response, severity):
        report = self.VulnerabilityReport(url, vulnerability_type, payload, http_request, http_response, severity)
        return report.to_json()