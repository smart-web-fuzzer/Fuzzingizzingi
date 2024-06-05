from bs4 import BeautifulSoup
import scrapy
from items import PacketFromDB


class SendToFuzzer:

    def __init__(self):
        self.from_db = PacketFromDB

    def send(self):
        for url, body in self.from_db.items():
            soup = BeautifulSoup(body, 'html.parser')
            forms = soup.find_all('form')

            for form in forms:
                attr = form.find_all('input')
                # input 속성이 존재 하면

                # 정해야 할 것!
                # 어떤 attr가 존재하면 어떤 퍼저 모듈로 보낼 것인지..?!

                #if attr == 'text':




            # 이 밑으로는 퍼저에게 보내는 동작 구현
            # 현재는 어떤 취약점을 어떻게 퍼징할 지 몰라 미구현

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



