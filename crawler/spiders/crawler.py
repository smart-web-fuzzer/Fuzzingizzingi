# crawler.py_0525_스팸패킷필터링
import scrapy
import tldextract
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import logging

class MySpider(scrapy.Spider):
    name = 'crawler'
    start_urls = ['http://www.itsecgames.com/']
    domain_origin = tldextract.extract(start_urls[0]).domain
#
    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.output = open('output.txt', 'w')
        self.seen_urls = set()  # 중복 URL 추적하기 위한 집합

    def parse(self, response):
        try:
            # URL 정규화
            normalized_url = self.normalize_url(response.url)

            if normalized_url not in self.seen_urls:
                # seen_urls 이용해 url 중복 안 되도록
                self.seen_urls.add(normalized_url)
                self.output.write(f'{normalized_url}\n')

                # 페이지에서 링크 추출
                img_links = response.xpath('//img/@src').extract()
                a_links = response.xpath('//a/@href').extract()
                links = img_links + a_links

                for link in links:
                    link = response.urljoin(link)
                    link = self.normalize_url(link)
                    link_domain = urlparse(link).netloc

                    if self.domain_origin in link_domain and link not in self.seen_urls:
                        self.seen_urls.add(link)
                        yield scrapy.Request(url=link, callback=self.parse)
                        print(f'수집한 URL : {link}')
                        self.output.write(f'{link}\n')

        except Exception as e:
            logging.error(f'Error detected in Function parse of main as {e}')

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)

        # 의미 없는 파라미터 제거 (random값 등)
        filtered_query = {k: v for k, v in query.items() if k not in ['random', 'session', 'timestamp']}
        normalized_query = urlencode(filtered_query, doseq=True)

        normalized_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            normalized_query,
            parsed_url.fragment
        ))
        return normalized_url

    def closed(self, reason):

        self.output.close()