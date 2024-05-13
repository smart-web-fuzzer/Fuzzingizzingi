# 다른 코드에서 import 하는 기능 추가 필요 
import re

class http_request_response_modifier:
    def __init__(self):
        pass

    def modify_request(self, request, rules):
        """HTTP 요청에 사용자 정의 규칙을 적용합니다."""
        for rule in rules:
            if 'block' in rule and rule['block']:
                if re.search(rule['pattern'], request):
                    return None  # 요청 차단
            else:
                request = re.sub(rule['pattern'], rule['replacement'], request)
        return request

    def modify_response(self, response, rules):
        """HTTP 응답에 사용자 정의 규칙을 적용합니다."""
        for rule in rules:
            response = re.sub(rule['pattern'], rule['replacement'], response)
        return response

# 사용 예제
modifier = http_request_response_modifier()

# 요청 수정 및 필터링 규칙
request_rules = [
    {'pattern': 'User-Agent: .*', 'replacement': 'User-Agent: CustomUserAgent/1.0'},
    {'pattern': 'GET /forbidden-path', 'replacement': '', 'block': True}
]

# 응답 수정 규칙
response_rules = [
    {'pattern': 'Server: .*', 'replacement': 'Server: CustomServer/1.0'},
    {'pattern': '<title>Old Title</title>', 'replacement': '<title>New Title</title>'}
]

# 수정 전 HTTP 요청
http_request = """GET / HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0

"""

# 수정 전 HTTP 응답
http_response = """HTTP/1.1 200 OK
Server: Apache/2.4.1 (Unix)
Content-Type: text/html

<html><head><title>Old Title</title></head><body>Content</body></html>
"""

# 요청 및 응답 수정
modified_request = modifier.modify_request(http_request, request_rules)
modified_response = modifier.modify_response(http_response, response_rules)

print("Modified HTTP Request:")
print(modified_request)
print("\nModified HTTP Response:")
print(modified_response)
