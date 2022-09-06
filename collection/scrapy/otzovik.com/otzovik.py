import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
import numpy as np
import urllib
import datetime

net_name = "ТЕХИНКОМ"
salon = "avtosalon_tehinkom_russia_moscow"

cookies = {
    'ROBINBOBIN': '1e9ca5cf706a5519c985179b7a',
    'ssid': '1060296627',
    'refreg': '1637936995~',
    '_ym_uid': '1637936996785785365',
    '_ym_d': '1637936996',
    '_ym_isad': '1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers',
}

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)

class YandexSpider(scrapy.Spider):
    name = 'otzovik'
    allowed_domains = ['otzovik.com']

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'AUTOTHROTTLE_ENABLED' : True,
        'AUTOTHROTTLE_START_DELAY' : 1,
        'AUTOTHROTTLE_MAX_DELAY' : 3,
    }

    def start_requests(self):
        yield Request(url="https://otzovik.com/reviews/" + salon + "/1/?order=date_desc", callback=self.parse_pages, headers=headers, cookies=cookies, dont_filter=True)

    def parse_pages(self,response):
        count = response.css("span.votes::text").extract_first()
        pages = math.ceil(float(count)/20)
        for i in range(1, pages + 1):
            yield Request(url="https://otzovik.com/reviews/" + salon + "/" + str(i) + "/?order=date_desc", callback=self.parse_page, headers=headers, cookies=cookies, dont_filter=True)

    def parse_page(self,response):
        full_link = response.css("a.review-read-link::attr(href)").extract()
        for link in full_link:
            yield Request(url="https://otzovik.com" + link, callback=self.parse_review, headers=headers, cookies=cookies, dont_filter=True)

    def parse_review(self,response):
        data = {}
        data['Сеть'] = net_name
        data['url_orig'] = response.url
        data['Автор'] = response.css("a.user-login > span::text").extract_first()
        data['Город'] = response.css("div.user-location::text").extract_first().split(",")[1].strip()
        data['Дата публикации'] = response.css(".review-postdate > span::text").extract_first().strip()
        data['Лайки'] = get_numbers(response.css("span.review-btn::text").extract_first())[0]
        data['Достоинства'] = response.css("div.review-plus::text").extract_first().strip()
        data['Недостатки'] = response.css("div.review-minus::text").extract_first().strip()
        data['Текст отзыва'] = response.css("div.description::text").extract_first().strip()
        # data['Адрес салона'] = response.css("")
        data['Общее впечатление'] = response.css(".summary::text").extract_first().strip()
        data['Оценка'] = get_numbers(response.css("div.product-rating::attr(title)").extract_first().strip())[0]
        yield data

       

















