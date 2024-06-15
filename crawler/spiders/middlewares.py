from scrapy.http import HtmlResponse
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import tldextract

class SeleniumMiddleware:
    def __init__(self):
        options = Options()
        options.headless = True

        # 프록시 설정 추가
        proxy = 'http://your_proxy:your_port'
        options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=options, service=Service('/path/to/your/chromedriver'))

    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            original_domain = self._get_domain(request.url)
            self.obj_click(original_domain)

            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'body')))

            body = self.driver.page_source
            spider.logger.info(f'Adding driver to meta for URL: {request.url}')
            # 'driver' 키를 메타데이터에 추가하여 반환
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request, meta={'driver': self.driver})

        except Exception as e:
            spider.logger.error(f'Error detected in Function process_request: {e}')
            return HtmlResponse(url=request.url, status=500, request=request)

    def obj_click(self, original_domain):
        try:
            onclick_elements = self.driver.find_elements(By.XPATH, '//*[@onclick]')
            elements = onclick_elements

            for element in elements:
                try:
                    current_domain = self._get_domain(self.driver.current_url)
                    if original_domain in current_domain:
                        element.click()
                except Exception as e:
                    print(f"Error clicking element: {e}")
                    continue

        except Exception as e:
            print(f'Error detected in Function obj_click: {e}')

    def _get_domain(self, url):
        return tldextract.extract(url).domain

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self):
        self.driver.quit()

