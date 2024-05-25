# 05.23
# pipelines.py
from scrapy.exceptions import DropItem

class DuplicateURLPipeline:
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        normalized_url = spider.normalize_url(item['url'])  # URL 정규화
        if normalized_url in self.seen_urls:
            raise DropItem(f"Duplicate URL found: {item['url']}")
        else:
            self.seen_urls.add(normalized_url)
            return item
            
class AWSDatabasePipeline:
    def process_item(self, item, spider):
        # AWS 데이터베이스에 저장하는 로직 추가
        pass