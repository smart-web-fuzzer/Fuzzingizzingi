# pipelines.py

from scrapy.exceptions import DropItem
import mysql.connector
from mysql.connector import errorcode
import logging

class DuplicateURLPipeline:
    def __init__(self, db_connection):
        self.seen_urls = set()  # 중복 URL을 확인하기 위한 집합
        self.db_connection = db_connection  # 데이터베이스 연결 객체
        self.cursor = db_connection.cursor()  # 데이터베이스 커서

    @classmethod
    def from_crawler(cls, crawler):
        # 크롤러 설정에서 데이터베이스 연결을 가져와 인스턴스화
        db_connection = mysql.connector.connect(
            host=crawler.settings.get('MYSQL_HOST'),  # MySQL 호스트
            database=crawler.settings.get('MYSQL_DATABASE'),  # 데이터베이스 이름
            user=crawler.settings.get('MYSQL_USER'),  # MySQL 사용자
            password=crawler.settings.get('MYSQL_PASSWORD')  # MySQL 비밀번호
        )
        return cls(db_connection)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        try:
            self.db_connection.commit()  # 변경 사항 커밋
        except Exception as e:
            logging.error(f"변경사항 커밋하는 중 오류 발생: {e}")
        finally:
            if self.db_connection.is_connected():
                self.cursor.close()
                self.db_connection.close()

    def process_item(self, spider, item):
        normalized_url = spider.normalize_url(item['url'])  # URL 정규화
        if normalized_url in self.seen_urls:
            raise DropItem(f"Duplicate URL found: {item['url']}")
        else:
            self.seen_urls.add(normalized_url)
            try:
                # 데이터베이스에 데이터 삽입
                insert_query = """
                INSERT INTO collected_urls (url)
                VALUES (%s)
                """
                data = (normalized_url,)
                self.cursor.execute(insert_query, data)
            except mysql.connector.Error as e:
                logging.error(f'Error {e} When Send URL to DB')
                self.db_connection.rollback()  # 오류 발생 시 롤백
            return item