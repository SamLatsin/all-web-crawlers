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

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

class YandexSpider(scrapy.Spider):
    name = 'spr'
    allowed_domains = ['www.spr.ru']
    start_urls = ['https://www.spr.ru/moskva/avtosaloni-avtotsentri/reviews/irbis-sever-23535.html']

    def parse(self,response):
        data = {}
        data['Сеть'] = "Ирбис"
        data['url_orig'] = response.url
        pages = 20
        for i in range(0, pages):
            cookies = {
                'PHPSESSID': 'jo9h7pliur3qrdlrob58vr03d6',
                '_ga': 'GA1.2.1808009514.1637912105',
                '_gid': 'GA1.2.1464767276.1637912105',
                '_ym_uid': '1637912105360680191',
                '_ym_d': '1637912105',
                '_ym_isad': '1',
                '_ym_visorc': 'w',
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Referer': 'https://www.spr.ru/moskva/avtosaloni-avtotsentri/reviews/irbis-sever-23535.html',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }
            params = (
                ('ajax', '1'),
                ('action', 'loadReviewsList'),
                ('id_firm', '23535'),
                ('id_net', '0'),
                ('page', str(i)),
            )
            yield Request(url="https://www.spr.ru/page/reviews/",cookies=cookies, 
                headers=headers, callback=self.parse_reviews, body=json.dumps(params), dont_filter=True)
    def parse_reviews(self,response):
        print(response)
        json = json.loads(response.text)
        html = json['content']
        print(html)
        yield response.text













