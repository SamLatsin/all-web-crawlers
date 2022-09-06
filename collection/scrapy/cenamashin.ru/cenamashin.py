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

url = "https://cenamashin.ru/autosalon/moskva/1014-otzyvy-pro-tehinkom-strogino.html"
net_name = "ТЕХИНКОМ"

cookies = {
    'mobile': '0',
    'PHPSESSID': '84e0aa07f1fc7660d3cb306118347913',
    'mob_block': '1',
    '_ym_uid': '1638007310493040256',
    '_ym_d': '1638007310',
    '_ym_isad': '1',
    '_ym_visorc': 'w',
    '_ga': 'GA1.2.1825524435.1638007310',
    '_gid': 'GA1.2.1672077895.1638007310',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Referer': 'https://cenamashin.ru/autosalon/sankt-peterburg/407-otzyvy-pro-avtodom.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

class YandexSpider(scrapy.Spider):
    name = 'cenamashin'
    allowed_domains = ['cenamashin.ru']

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 1,
    #     'AUTOTHROTTLE_ENABLED' : True,
    #     'AUTOTHROTTLE_START_DELAY' : 1,
    #     'AUTOTHROTTLE_MAX_DELAY' : 3,
    # }

    def start_requests(self):
        yield Request(url=url, callback=self.parse_pages, headers=headers, cookies=cookies, dont_filter=True, meta={"id_":get_numbers(url)[0]})

    def parse_pages(self,response):
        count = get_numbers(response.css("div.data-block:nth-child(22) > h2::text").extract_first())[0]
        pages = math.ceil(float(count)/10)
        # test
        # pages = 1
        for i in range(1, pages + 1):
            params = (
                ('id', str(response.meta.get("id_"))), # 
                ('m', '0'),
                ('act', '1'),
                ('page', str(i)),
            )
            yield Request(url="https://cenamashin.ru/ajax/salon_show_otzyvs_next.php?" + urllib.parse.urlencode(params), callback=self.parse_page, headers=headers, cookies=cookies, dont_filter=True)

    def parse_page(self,response):
        # print(response.text)
        data = {}
        data['Сеть'] = net_name
        data['url_orig'] = response.url

        authors    = response.css("table > tr:nth-child(1) > td:nth-child(1) > span > a > b::text").extract()
        dates      = response.css("table > tr:nth-child(1) > td:nth-child(1) > span > small::text").extract()
        texts      = response.css("table > tr:nth-child(1) > td:nth-child(2) > div::text").extract()
        likes      = response.css("table > tr:nth-child(1) > td:nth-child(1) > span > div > span > small:nth-child(4)::text").extract()
        dislikes   = response.css("table > tr:nth-child(1) > td:nth-child(1) > span > div > span > small:nth-child(6)::text").extract()

        for id,author in enumerate(authors):
            data['Автор'] = authors[id].strip()
            data['Дата публикации'] = dates[id*2].strip()
            data['Текст отзыва'] = texts[id].strip()
            data['Текст отзыва'] = data['Текст отзыва'].replace("\r\n", " ")
            data['Лайки'] = get_numbers(likes[id])[0].strip()
            data['Дизлайки'] = get_numbers(dislikes[id])[0].strip()
            yield data
        

       

















