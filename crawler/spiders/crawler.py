#crawler.py


import scrapy
import tldextract
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import logging

class MySpider(scrapy.Spider):
    name = 'cloud'

    def __init__(self, start_url=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)

        if start_url:
            self.start_urls = [start_url]
        else:
            raise ValueError("No start URL provided")

        self.domain_origin = tldextract.extract(self.start_urls[0]).domain
        self.output = open('output.txt', 'w')
        self.seen_urls = set()

    def parse(self, response):
        try:
            # response.headers.get('Content-Type') 사용해 응답이 텍스트인지 확인 후, 텍스트 아닌 경우 return 호출해 처리 건너뜀. 이미지나 다른 형식의 응답 처리하는 중 발생하는 오류 방지
            if not response.headers.get('Content-Type', b'').startswith(b'text'):
                # Skip non-text responses
                return

            normalized_url = self.normalize_url(response.url)

            if normalized_url not in self.seen_urls:
                self.seen_urls.add(normalized_url)
                self.output.write(f'{normalized_url}\n')

                a_links = response.xpath('//a/@href').extract()

                for link in a_links:
                    link = response.urljoin(link)
                    link = self.normalize_url(link)
                    link_domain = urlparse(link).netloc

                    if self.domain_origin in link_domain and link not in self.seen_urls:
                        yield scrapy.Request(url=link, callback=self.parse)

        except Exception as e:
            logging.error(f'Error detected in Function parse: {e}')

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
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