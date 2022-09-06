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
    name = 'kitabu'
    allowed_domains = ['otzyvy.kitabi.ru']
    start_urls = ['http://otzyvy.kitabi.ru/kompaniya/rolf?page=2']

    def parse(self,response):
        data = {}
        data['Сеть'] = "РОЛЬФ"
        data['url_orig'] = response.url
        names = response.css("div.reviews-list2-item-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)::text").extract()
        texts_all = response.css("div.reviews-list2-item-container div.reviews-list2-item-text").extract()
        dates = response.css("span.reviews-list-item-date::text").extract()   
        ratings = response.css("div.reviews-list2-item-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)::text").extract()
        for id,name in enumerate(names):
            data['Имя'] = names[id].strip()
            data['Текст отзыва'] = remove_tags(texts_all[id]).strip()
            data['Дата отзыва'] = dates[id].strip()
            if ratings[id].strip() == "Хорошо!":
                data['Оценка'] = "Положительная"
            else:
                data['Оценка'] = "Отрицательная"
            yield data
         

       

















