from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time

class SeleniumMiddleware:
    def __init__(self):
        options = Options()
        options.headless = True  # 브라우저 창을 숨기는 옵션
        self.driver = webdriver.Chrome(options=options, service=Service('chromedriver.exe'))

    def process_request(self, request, spider):
        self.driver.get(request.url)
        self.obj_click()

        # 페이지가 완전히 로드될 때까지 기다립니다.
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'body')))

        body = self.driver.page_source
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def obj_click(self): # click 가능한 객체 클릭하는 함수

        # `onclick` 속성이 있는 모든 요소를 찾습니다.
        onclick_elements = self.driver.find_elements(By.XPATH, '//*[@onclick]')

        # 'img' 속성이 있는 모든 요소를 찾습니다.
        img_elements = self.driver.find_elements(By.XPATH, '//img')  # --> 이거 img src 있는 거만 클릭하도록 수정

        # 'span' 클래스에 있는 문자열을 찾습니다. --> 리소스 낭비 같아서 일단 보류
        # span_elements = self.driver.find_elements()

        elements = onclick_elements + img_elements  # onclick 객체 + img src 객체 리스트

        for element in elements:
            try:
                element.click()  # 각 요소를 클릭
                # 클릭 후 충분한 반응 시간을 기다립니다.
                time.sleep(2)
            except Exception as e:
                print(f"Error clicking element: {e}")
                continue

    def form_input(self): # form 태그에 값 넣는 함수
        form_elements = self.driver.find_elements(By.)


    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self):
        self.driver.quit()