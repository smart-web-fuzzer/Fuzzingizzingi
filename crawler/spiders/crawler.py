# crawler.py_javascript+proxy
import scrapy
import tldextract
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import logging
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MySpider(scrapy.Spider):
    name = 'crawler'

    def __init__(self, start_url=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)

        if start_url:
            self.start_urls = [start_url]  # 시작URL 설정
        else:
            raise ValueError("No start URL provided")  # 시작URL 없을 경우 예외 발생

        self.domain_origin = tldextract.extract(self.start_urls[0]).domain  # 도메인 추출
        self.output = open('output.txt', 'w')  # 출력파일 열기
        self.seen_urls = set()  # 수집된 URL 저장할 집합

        # Selenium WebDriver 초기화
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 헤드리스 모드로 실행
        
        # 프록시 설정 추가
        proxy = 'http://your_proxy:your_port'
        chrome_options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        try:
            content_type = response.headers.get('Content-Type', b'').decode('utf-8')
            logging.debug(f'Content-Type for {response.url}: {content_type}')

            if not content_type.startswith('text'):
                logging.debug(f'Skipped non-text content: {response.url}')
                return  # 텍스트 콘텐츠가 아닌 경우 스킵

            normalized_url = self.normalize_url(response.url)  # URL 정규화

            if normalized_url not in self.seen_urls:
                self.seen_urls.add(normalized_url)  # 수집된 URL에 추가
                self.output.write(f'{normalized_url}\n')  # 파일에 URL 기록
                logging.debug(f'수집된 URL: {normalized_url}')

                a_links = response.xpath('//a/@href').extract()  # 페이지 내 모든 링크 추출
                logging.debug(f'Found {len(a_links)} links on {response.url}')

                for link in a_links:
                    link = response.urljoin(link)  # 상대URL을 절대URL로 변환
                    link = self.normalize_url(link)  # URL 정규화
                    link_domain = urlparse(link).netloc

                    if self.domain_origin in link_domain and link not in self.seen_urls:
                        logging.debug(f'Yielding request for: {link}')
                        yield scrapy.Request(url=link, callback=self.parse)  # 링크에 대한 요청 생성

                # Selenium 사용해 JavaScript 이벤트 트리거
                logging.debug(f'Processing with Selenium for URL: {response.url}')
                self.driver.get(response.url)
                self.trigger_js_events()  # JavaScript 이벤트 트리거

                # 업데이트된 페이지 소스로 새로운 응답 객체 생성
                updated_body = self.driver.page_source
                updated_response = HtmlResponse(
                    url=response.url, 
                    body=updated_body, 
                    encoding='utf-8',
                    headers={'Content-Type': 'text/html'}  # Content-Type 명시적으로 추가
                )
                logging.debug(f'Updated body length: {len(updated_body)}')

                # 업데이트된 콘텐츠로 페이지 재파싱
                yield from self.parse(updated_response)

        except Exception as e:
            logging.error(f'Error detected in Function parse: {e}')

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        filtered_query = {k: v for k, v in query.items() if k not in ['random', 'session', 'timestamp']}  # 특정 쿼리 매개변수 제거
        normalized_query = urlencode(filtered_query, doseq=True)

        normalized_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            normalized_query,
            parsed_url.fragment
        ))
        logging.debug(f'Normalized URL: {normalized_url}')
        return normalized_url

    def trigger_js_events(self):
        try:
            # JavaScript를 실행하여 모든 onclick 이벤트 리스너 트리거
            initial_url = self.driver.current_url
            logging.debug(f'Triggering JS events on: {initial_url}')
            self.driver.execute_script("""
                var elements = document.querySelectorAll('*');
                elements.forEach(function(element) {
                    element.addEventListener('click', function(event) {
                        event.stopPropagation();
                        event.preventDefault();
                    }, true);

                    if (typeof element.onclick == 'function') {
                        element.click();  # onclick 이벤트 트리거
                    }
                });
            """)

            # 페이지 이동 발생 시 이전 페이지로 돌아감
            try:
                WebDriverWait(self.driver, 10).until(EC.url_changes(initial_url))
                logging.debug(f'URL changed from {initial_url}')
                self.driver.back()
            except Exception as e:
                logging.debug(f'No URL change detected: {e}')
                self.handle_no_url_change(initial_url)  # URL 변경되지 않은 경우 처리

        except Exception as e:
            logging.error(f'Error triggering JS events: {e}')

    def handle_no_url_change(self, url):
        # URL 변경되지 않은 경우 해당 URL 수집
        logging.debug(f'Handling no URL change for: {url}')
        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.output.write(f'No change: {url}\n')

    def closed(self, reason):
        self.output.close()  # 출력 파일 닫기
        self.driver.quit()