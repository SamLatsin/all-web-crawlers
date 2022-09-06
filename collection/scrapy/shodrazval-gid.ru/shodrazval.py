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

class YandexSpider(scrapy.Spider):
    name = 'shodrazval'
    allowed_domains = ['shodrazval-gid.ru']
    start_urls = ['https://shodrazval-gid.ru/adresa/moskva/avtoport-n1371/']

    def parse(self,response):
        data = {}
        data['url_link'] = "https://auto.ru/diler/cars/all/bmw_avtoport_moskva"
        data['url_orig'] = response.url
        names = response.css("div.otz_block > h4:nth-child(1)::text").extract()
        texts = response.css("div.otz_block > .otz_text::text").extract()
        dates = response.css("div.otz_block > .otz_date > span::text").extract()   
        for id,name in enumerate(names):
            data['Имя'] = names[id]
            data['Текст отзыва'] = texts[id]
            data['Дата отзыва'] = (datetime.datetime.now() - datetime.timedelta(days=int(get_numbers(dates[id])[0])*365)).strftime("%Y-%m-%d %H:%M:%S")
            yield data
         

       

















