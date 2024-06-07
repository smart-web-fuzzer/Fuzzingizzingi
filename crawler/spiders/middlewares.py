# middlewares.py

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import logging
import tldextract


class SeleniumMiddleware:
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options, service=Service('chromedriver.exe'))

    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            original_domain = self._get_domain(request.url)
            self.obj_click(original_domain)

            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'body')))
            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
        except Exception as e:
            logging.error(f'Error detected in Function process_request as {e}')

    def obj_click(self, original_domain):
        try:
            onclick_elements = self.driver.find_elements(By.XPATH, '//*[@onclick]')
            img_elements = self.driver.find_elements(By.XPATH, '//img')
            elements = onclick_elements + img_elements

            if elements:
                for element in elements:
                    try:
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
