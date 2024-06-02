# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CrawledURL(scrapy.item):
    url = scrapy.Field()

class PacketFromDB(scrapy.item):
    url = scrapy.Field()
    body = scrapy.Field()