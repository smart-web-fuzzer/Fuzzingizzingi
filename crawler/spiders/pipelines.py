from scrapy.exceptions import DropItem
import mysql.connector
from mysql.connector import errorcode
from items import PacketFromDB
from items import CrawledURL
import logging

class DuplicateURLPipeline:
    def __init__(self, host, database, user, password):
        self.seen_urls = set()
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings.get('MYSQL_HOST')
        database = crawler.settings.get('MYSQL_DATABASE')
        user = crawler.settings.get('MYSQL_USER')
        password = crawler.settings.get('MYSQL_PASSWORD')
        return cls(host, database, user, password)

    def open_spider(self, spider):
        try:
            # MySQL 데이터베이스에 연결
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()

        except errorcode as e:
            spider.logger.error(f"Error while connecting to MySQL: {e}")

    def close_spider(self, spider):

        if self.connection.is_connected():
            # 데이터베이스 저장 커밋하기
            self.connection.commit()
            self.cursor.close()
            # 데이터베이스 연결 닫기
            self.connection.close()

    def process_item(self, spider):
        # URL 정규화
        normalized_url = spider.normalize_url(CrawledURL['url'])
        if normalized_url in self.seen_urls:
            raise DropItem(f"Duplicate URL found: {CrawledURL['url']}")

        else:
            self.seen_urls.add(normalized_url)

            try:

                # 데이터 삽입
                insert_query = """
                INSERT INTO collected_urls (url)
                VALUES (%s)
                """
                data = (normalized_url,)

                self.cursor.execute(insert_query, data)
                self.connection.commit()

            except errorcode as e:
                logging.error(f'Error {e} When Send URL to DB')
                # 롤백 추가
                self.connection.rollback()

            return CrawledURL