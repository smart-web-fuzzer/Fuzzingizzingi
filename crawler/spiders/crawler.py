import scrapy
import tldextract as tld
import re
from urllib.parse import urlparse


class MySpider(scrapy.Spider):
    name = 'cloud'
    start_urls = ['https://notelass.site/introduce']
    domain_origin = tld.extract(start_urls[0]).domain

    def parse(self, response):
        # 페이지에서 링크 추출
        links = response.xpath('//a/@href').extract()
        for link in links:
            link_domain = urlparse(link).netloc
            if self.domain_origin in link_domain: # 최상위 url의 도메인과 같아야 크롤링
                yield response.follow(link, self.parse)
                print(f'!!!URL!!! : {link}')
                
# 현재 코드는 a href 부분 url만 파싱 해서 탐색중
# a href, img onclick, img onerror, img onlocation, div href, span은 모두 click 시도
# 파일로 저장하는 것도 구현해서 코드 커버리지 확인 해봐야 함
#





# 구현해야 할 것들
# 1. 최상위 url에서 <a>태그 뽑아서 재귀적으로 url 탐색
# 2. 탐색 과정에서 selenium으로 onclick 가능한 객체들 클릭하면서 url 탐색
# --> 멀티스레딩을 사용해야 하나?
#
# 3. 프록시에서 가져온 태그들에 대한 취약점 분석