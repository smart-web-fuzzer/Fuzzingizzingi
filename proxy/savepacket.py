import json
import urllib.parse
import mysql.connector

# MySQL 연결 설정
config = {
    'user': 'zzingzzingi',
    'password': '!Ru7eP@ssw0rD!12',
    'host': 'localhost',
    'port': 5555,
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
                request_line, headers_alone = raw_data.split(b'\r\n', 1)
                headers, body = headers_alone.split(b'\r\n\r\n', 1)
            except ValueError:
                continue

            request_line = request_line.decode('iso-8859-1')
            headers = headers.decode('iso-8859-1')
            body = body.decode('iso-8859-1')

            request_parts = request_line.split()
            if len(request_parts) < 3:
                continue

            method, url, version = request_parts
            parsed_url = urllib.parse.urlsplit(url)
            params = urllib.parse.parse_qs(parsed_url.query)

            headers_dict = {}
            for header_line in headers.split('\r\n'):
                key, value = header_line.split(': ', 1)
                headers_dict[key] = value

            cookies = headers_dict.get('Cookie', '')
            cookies_dict = urllib.parse.parse_qs(cookies.replace('; ', '&'))

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

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print("Packets saved to the database")
