import json
import urllib.parse
import mysql.connector

# MySQL 연결 설정
config = {
    'user': 'zzingzzingi',
    'password': '!Ru7eP@ssw0rD!12',
    'host': '13.209.63.65',
    'database': 'Fuzzingzzingi',
}

# DB에 패킷 데이터 저장
def save_packet_to_db(packet_storage):
    try:
        # 설정 사용하여 DB에 연결하고 커서 생성 
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # 패킷 데이터를 순회하며 데이터 추출
        for raw_data in packet_storage:
            try:
                # request_line, headers_alone으로 분리 
                request_line, headers_alone = raw_data.split(b'\r\n', 1)
                # headers_alone 을 다시 headers, body로 분리
                headers, body = headers_alone.split(b'\r\n\r\n', 1)
            except ValueError:
                continue

            # 각 데이터 부분을 sio-8859-1 인코딩을 사용하여 디코딩 실시 
            request_line = request_line.decode('iso-8859-1')
            headers = headers.decode('iso-8859-1')
            body = body.decode('iso-8859-1')

            # request_line을 공백을 기준으로 분리하여 method, url, version으로 나눔
            request_parts = request_line.split()
            if len(request_parts) < 3:
                continue

            method, url, version = request_parts
            parsed_url = urllib.parse.urlsplit(url)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            
            # 헤더를 딕셔너리로 변환, 만약 쿠키가 존재하면 파싱하여 딕셔너리로 변환 
            headers_dict = {}
            for header_line in headers.split('\r\n'):
                key, value = header_line.split(': ', 1)
                headers_dict[key] = value

            cookies = headers_dict.get('Cookie', '')
            cookies_dict = urllib.parse.parse_qs(cookies.replace('; ', '&'))


            # 데이터를 MySQL에 삽입
            # insert_query = 를 사용하여 requests 테이블에 데이터 삽입하는 SQL 쿼리 정의 
            insert_query = """
                INSERT INTO requests (url, parameters, method, protocol_version, headers, cookies, response_body)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # 쿼리를 실행하고 데이터 삽입, 삽입 데이터는 JSON 형식으로 변환하여 저장 
            cursor.execute(insert_query, (
                url,
                json.dumps(params),
                method,
                version,
                json.dumps(headers_dict),
                json.dumps(cookies_dict),
                body
            ))

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

    print("Packets saved to the database")

# Example usage
# save_packet_to_db(CustomProxyRequestHandler.packet_storage)
