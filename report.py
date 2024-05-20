import json
from datetime import datetime

class VulnerabilityReport:
    def __init__(self, url, vulnerability_type, payload, http_request, http_response, severity):
        self.url = url
        self.vulnerability_type = vulnerability_type
        self.severity = severity
        self.payload = payload
        self.http_request = http_request
        self.http_response = http_response

    def to_dict(self):
        return {
            "URL": self.url,
            "Vulnerability Type": self.vulnerability_type,
            "Severity": self.severity,
            "Payload": self.payload,
            "HTTP Request": self.http_request,
            "HTTP Response": self.http_response,
        }
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)