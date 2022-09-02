import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math

import json

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

class AvtodomSpider(scrapy.Spider):
    name = 'avtodom'
    allowed_domains = ['avtodom.ru']
    start_urls = ["https://avtodom.ru/allcars/?PAGEN_1=1"]

    def parse(self, response):
        # test
        # yield Request("https://avtodom.ru/stock/bmw/m235i-xdrive-gran-kupe/0101058432/", callback=self.parse_car)     
        

        # production
        pages = response.css("li.pagination__item:nth-child(7) > a:nth-child(1)::text").extract_first()
        for i in range(1, int(pages) + 1):
            yield Request("https://avtodom.ru/allcars/?PAGEN_1=" + str(i), callback=self.parse_page)

    def parse_page(self, response):
        links = response.css("div.catalog-items__item > div:nth-child(1) > a:nth-child(2)::attr(href)").extract()
        for link in links:
            link = "https://avtodom.ru" + link
            yield Request(link, callback=self.parse_car)        

    def parse_car(self, response):
        data = {}
        data['url'] = response.request.url
        for response in response.css("body"):
            try:
                data['Фото'] = ""
                photos = response.css("div.stock-product-gallery__item > a:nth-child(1) > img:nth-child(1)::attr(src)").extract()
                photos = set(photos)
                for photo in photos:
                    data['Фото'] += "https://avtodom.ru" + photo.replace(" ",  "%20") + ","
                data['Фото'] = data['Фото'][:-1]
            except Exception:
                data['Фото'] = ""

            try:
                data['Номер ТС'] = get_numbers(response.css("div.-desktop::text").extract_first())[0]
            except Exception:
                data['Номер ТС'] = ""

            try:
                data['Теги'] = ""
                tags = response.css("div.stock-product-advantages__item > div:nth-child(1)::text").extract()
                for tag in tags:
                    data['Теги'] += tag + ","
                data['Теги'] = data['Теги'][:-1]
            except Exception:
                data['Теги'] = ""

            try:
                data['Наличие'] = response.css(".stock-product__status::text").extract_first().strip().replace("Наличие: ","")
            except Exception:
                data['Наличие'] = ""


            try:
                data['Дилерский центр'] = response.css(".stock-product-avail__link::attr(href)").extract_first()
            except Exception:
                data['Дилерский центр'] = ""

            try:
                data['Стоимость'] = "".join(get_numbers(response.css("div.stock-product-price__item:nth-child(1) > div:nth-child(2) > span:nth-child(1)::text").extract_first()))
            except Exception:
                data['Стоимость'] = ""

            try:
                data['Специальная цена'] = "".join(get_numbers(response.css("div.stock-product-price__item:nth-child(2) > div:nth-child(2) > span:nth-child(1)::text").extract_first()))
            except Exception:
                data['Специальная цена'] = ""

            keys_strong = ['Выгода Trade-In', 'Выгода при оформлении КАСКО', 'Выгода при покупке в кредит', 'Выгода при страховании', 'Выгода при покупке доп. оборудования']
            for key in keys_strong:
                data[key] = ""

            try:
                keys = response.css("div.stock-product-special__item > div:nth-child(1) > span:nth-child(1)::text").extract()
                for id,key in enumerate(keys):
                    keys[id] = key.strip()
                keys = list(filter(None, keys))
                # print(keys)
            except Exception:
                keys = []

            values = response.css("div.stock-product-special__item > div:nth-child(1) > div:nth-child(2)::text").extract()
            for id,value in enumerate(values):
                values[id] = value.strip()
            values = list(filter(None, values))

            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = "".join(get_numbers(values[id].strip()))
                        except Exception:
                            data[key1] = ""

            data['Марка'] = response.css("li.breadcrumbs__item:nth-child(3) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
            title = response.css("h1.stock-product__title::text").extract_first()
            kuzov = response.css("div.stock-product-parameters__item:nth-child(2) > div:nth-child(2)::text").extract_first()
            data['Модель'] = title.replace(data['Марка'], "").strip().split(" ")[0]
            data['Комплектация'] = " ".join(title.replace(data['Модель'], "").replace(data['Марка'], "").strip().split(" ")[0:])

            keys_strong = ['Тип двигателя', 'КПП', 'Тип кузова', 'Тип привода', 'Объем л.', 'Мощность', 'Пробег', 'Год выпуска', 'Размеры', 'Цвет кузова', 'Цвет салона']
            for key in keys_strong:
                data[key] = ""

            try:
                keys = response.css("li.stock-product-description__item > div:nth-child(1)::text").extract()
                for id,key in enumerate(keys):
                    keys[id] = key.strip()
                keys = list(filter(None, keys))
                # print(keys)
            except Exception:
                keys = []

            values = response.css("li.stock-product-description__item > div:nth-child(2)::text").extract()
            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""
            if data['Размеры'] != "":
                try:
                    data['Длина кузова (мм)'] = data['Размеры'].split("*")[0]
                    data['Ширина кузова (мм)'] = data['Размеры'].split("*")[1]
                    data['Высота кузова (мм)'] = data['Размеры'].split("*")[2]
                except Exception:
                    try:
                        data['Длина кузова (мм)'] = data['Размеры'].split("/")[0]
                        data['Ширина кузова (мм)'] = data['Размеры'].split("/")[1]
                        data['Высота кузова (мм)'] = data['Размеры'].split("/")[2]
                    except Exception:
                        try:
                            data['Длина кузова (мм)'] = data['Размеры'].split("x")[0] # русская х
                            data['Ширина кузова (мм)'] = data['Размеры'].split("x")[1]
                            data['Высота кузова (мм)'] = data['Размеры'].split("x")[2]
                        except Exception:
                            data['Длина кузова (мм)'] = data['Размеры'].split("х")[0] # английский х
                            data['Ширина кузова (мм)'] = data['Размеры'].split("х")[1]
                            data['Высота кузова (мм)'] = data['Размеры'].split("х")[2]
            else:
                data['Длина кузова (мм)'] = ""
                data['Ширина кузова (мм)'] = ""
                data['Высота кузова (мм)'] = ""
            del data['Размеры']

            data['Описание'] = ""
            desc = response.css(".comp-listing > ul:nth-child(1) > li::text").extract()
            for des in desc:
                data['Описание'] += des + ","
            if len(data['Описание']) > 1:
                data['Описание'] = data['Описание'][:-1]

            data['Другие варианты в наличии'] = ""
            desc = response.css("div.stock-product-slider__item > div > a::attr(href)").extract()
            for des in desc:
                data['Другие варианты в наличии'] += "https://avtodom.ru" + des + ","
            if len(data['Другие варианты в наличии']) > 1:
                data['Другие варианты в наличии'] = data['Другие варианты в наличии'][:-1]
            yield data













