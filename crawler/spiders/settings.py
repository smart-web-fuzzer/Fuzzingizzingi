# settings.py

# BOT_NAME = 'Myproject'

SPIDER_MODULES = ['Myproject.spiders']
NEWSPIDER_MODULE = 'Myproject.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Myproject (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# DEBUG 레벨 이상의 로그 설정
LOG_LEVEL = 'DEBUG'

DOWNLOAD_TIMEOUT = 30
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
     'scrapy.spidermiddlewares.referer.RefererMiddleware': None,
     'Myproject.middlewares.SeleniumMiddleware': 543,
 }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
    'Myproject.middlewares.SeleniumMiddleware': 800,
    # 경로 바뀌면 이것도 바꿔야 함
}

# 프록시 설정
PROXY = 'http://your_proxy:your_port'

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines-비활성화 시(현재) 크롤링된 상태 그대로 남음(추가처리나 저장X), 활성화 시 후처리나 저장o
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Myproject.pipelines.DuplicateURLPipeline': 100,
    # 'pipelines.AWSDatabasePipeline': 200,
    # 경로 바뀌면 이것도 바꿔야 함
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# MySQL 데이터베이스 연결 설정
MYSQL_HOST = '13.209.63.65'  # 실제 MySQL 호스트로 변경
MYSQL_DATABASE = 'Fuzzingzzingi'  # 실제 데이터베이스 이름으로 변경
MYSQL_USER = 'zzingzzingi'  # 실제 데이터베이스 사용자로 변경
MYSQL_PASSWORD = '!Ru7eP@ssw0rD!1'  # 실제 데이터베이스 비밀번호로 변경


from shutil import which
# Selenium 관련 설정
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS=['--headless']  # 브라우저 숨기는 옵션 등 추가 가능