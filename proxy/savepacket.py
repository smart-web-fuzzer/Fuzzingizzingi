import json
import urllib.parse
import mysql.connector

# MySQL 연결 설정
config = {
    'user': 'zzingzzingi',  # MySQL 사용자명
    'password': '!Ru7eP@ssw0rD!12',  # MySQL 비밀번호
    'host': '13.209.63.65',  # MySQL 서버 호스트
    'database': 'Fuzzingzzingi',  # 데이터베이스 이름
}

# DB 연결 테스트
def test_db_connection():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Database connection successful")
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# DB에 패킷 데이터 저장
def save_packet_to_db(packet_storage):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        print("Database connection established for saving packets")

        insert_query = """
            INSERT INTO requests (url, parameters, method, protocol_version, headers, cookies, response_body)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for packet in packet_storage:
            cursor.execute(insert_query, (
                packet['url'],
                json.dumps(packet['parameters']),
                packet['method'],
                packet['protocol_version'],
                json.dumps(packet['headers']),
                json.dumps(packet['cookies']),
                packet['response_body']
            ))
            print("Data inserted into database")

        connection.commit()
        print("Database commit successful")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Database connection closed")

    print("Packets saved to the database")

# 테스트
if __name__ == "__main__":
    test_db_connection()