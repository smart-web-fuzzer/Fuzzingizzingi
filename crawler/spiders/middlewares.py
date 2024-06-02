from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import logging
import tldextract


class SeleniumMiddleware:
    def __init__(self):
        options = Options()
        options.headless = True  # 브라우저 창 숨기는 옵션
        # options.add_argument("--disable-popup-blocking")  # 팝업 차단 비활성화
        # options.add_argument("--disable-notifications")  # 알림 차단

        self.driver = webdriver.Chrome(options=options, service=Service('chromedriver.exe'))

    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            original_domain = self._get_domain(request.url)
            # self.form_input()
            self.obj_click(original_domain)

            # 페이지가 완전히 로드될 때까지 기다립니다.
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'body')))

            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

        except Exception as e:
            logging.error(f'Error detected in Function process_request as {e}')

    # def form_input(self): # form 태그에 값 넣는 함수
    #     try:
    #         form_elements = self.driver.find_elements(By.TAG_NAME, 'input')
    #         image_path = 'zingzing.png'
    #
    #         if form_elements: # form 태그가 존재한다면
    #             for element in form_elements:
    #                 input_type = element.get_attribute('type')  # type 속성을 가져옵니다.
    #
    #                 # 문자열 입력하는 폼 태그들
    #                 if input_type == 'text':
    #                     element.send_keys('Fuzingzing')
    #                     print('입력했음!')
    #                 elif input_type == 'password':
    #                     element.send_keys('Fuzingzing')
    #                 elif input_type == 'number':
    #                     element.send_keys('119')
    #                 elif input_type == 'search':
    #                     element.send_keys('Fuzingzing')
    #
    #                 # file, image 업로드 하는 태그들
    #                 elif input_type == 'file':
    #                     element.send_keys(image_path)
    #
    #                 # checkbox 같은 것들
    #                 elif input_type == 'checkbox':
    #                     element.click()
    #                 elif input_type == 'radio':
    #                     element.click()
    #
    #                 # button, submit
    #                 elif input_type == 'button':
    #                     element.click()
    #                 elif input_type == 'submit':
    #                     element.click()
    #
    #             print(f'heyheyhey{form_elements}')
    #
    #     except Exception as e:
    #         logging.error(f'Error detected in Function form_input as {e}')

    def obj_click(self, original_domain):  # click 가능한 객체 클릭 하는 함수
        try:
            onclick_elements = self.driver.find_elements(By.XPATH, '//*[@onclick]')
            img_elements = self.driver.find_elements(By.XPATH, '//img')
            elements = onclick_elements + img_elements

            if elements:
                for element in elements:

                    try:
                        # time.sleep(1)
                        onclick_domain = element.get_attribute('href')
                        current_domain = self._get_domain(self.driver.current_url)
                        if current_domain in original_domain and current_domain in onclick_domain:
                            element.click()

                    except Exception as e:
                        print(f"Error clicking element: {e}")
                        continue
        except Exception as e:
            print(f'Error detected in Function obj_click as {e}')

    def _get_domain(self, url):
        return tldextract.extract(url).domain

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self):
        self.driver.quit()


