import json
import urllib.parse
import mysql.connector

# MySQL 연결 설정
config = {
    'user': 'zzingzzingi',
    'password': '!Ru7eP@ssw0rD!12',
    'host': '13.209.63.65',
    'port': 3306,  # MySQL 기본 포트
    'database': 'Fuzzingzzingi',
}

def save_packet_to_db(packet_storage):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        for raw_data in packet_storage:
            try:
                parts = raw_data.split(b'\r\n\r\n', 1)
                headers_alone = parts[0]
                body = parts[1] if len(parts) > 1 else b''

                header_lines = headers_alone.split(b'\r\n')
                request_line = header_lines[0]
                headers = b'\r\n'.join(header_lines[1:])

                request_line = request_line.decode('iso-8859-1')
                headers = headers.decode('iso-8859-1')
                body = body.decode('iso-8859-1')

                request_parts = request_line.split(maxsplit=2)
                if len(request_parts) != 3:
                    print(f"Invalid request line: {request_line}")
                    continue

                method, url, version = request_parts
                parsed_url = urllib.parse.urlsplit(url)
                params = urllib.parse.parse_qs(parsed_url.query)

                headers_dict = {}
                for header_line in headers.split('\r\n'):
                    if ': ' in header_line:
                        key, value = header_line.split(': ', 1)
                        headers_dict[key] = value

                cookies = headers_dict.get('Cookie', '')
                cookies_dict = urllib.parse.parse_qs(cookies.replace('; ', '&'))

                # 데이터베이스 컬럼 크기 조정 (필요시 데이터 잘라내기)
                method = method[:10]  # method 컬럼 크기 제한
                url = url[:2048]       # url 컬럼 크기 제한

                try:
                    # 데이터를 MySQL에 삽입
                    insert_query = """
                        INSERT INTO requests (url, parameters, method, protocol_version, headers, cookies, response_body)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        url,
                        json.dumps(params),
                        method,
                        version,
                        json.dumps(headers_dict),
                        json.dumps(cookies_dict),
                        body
                    ))
                except mysql.connector.Error as err:
                    print(f"Error inserting packet into database: {err}")

            except Exception as e:
                print(f"Error parsing packet: {e}")
                continue

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print("Packets saved to the database")
