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

class KiaArmandSpider(scrapy.Spider):
    name = 'kia-armand'
    allowed_domains = ['kia-armand.ru']
    start_urls = ["https://kia-armand.ru/buy/cars/"]

    def parse(self, response):
        links = response.css("div.car-card > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)::attr(href)").extract()

        # test
        # yield Request("https://kia-armand.ru/models/rio/cars/ae19b6897a4ff62b92bded3a4c06046b/", callback=self.parse_car)

        for link in links:
            link = "https://kia-armand.ru" + link
            yield Request(link, callback=self.parse_cars)


    def parse_cars(self, response):
        links = response.css("div.catalog-element > div:nth-child(2) > h3:nth-child(1) > a:nth-child(1)::attr(href)").extract()
        for link in links:
            link = "https://kia-armand.ru" + link
            yield Request(link, callback=self.parse_car)           

    def parse_car(self, response):
        data = {}
        data['url'] = response.request.url
        for response in response.css("body"):

            keys_strong = ['Город, г/км', 'Трасса, г/км', 'В комбинированном цикле, г/км', 'Двигатель', 'Мощность, л.с.', 'Крутящий момент, Н·м', 'Тип топлива', 'Рабочий объем, л', 'Рабочий объем, см3', 'Экологический класс', 'Коробка передач', 'Привод', 'Время разгона 0-100 км/ч, с', 'Расход топлива комбинированный, л/100 км', 'Тип кузова', 'Габариты (длина/ширина/высота), мм', 'Колесная база, мм', 'Дорожный просвет, мм', 'Объём багажника (VDA), л', 'Код модели', 'OCN', 'Модельный год', 'Год производства']
            for key in keys_strong:
                data[key] = ""

            try:
                keys = response.css("div.info-section > div > div > div > dl > dt:nth-child(1)::text").extract()
                for id,key in enumerate(keys):
                    keys[id] = key.strip()
                keys = list(filter(None, keys))
                # print(keys)
            except Exception:
                keys = []

            values = response.css("div.info-section > div > div > div > dl > dd:nth-child(2)::text").extract()
            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""

            data['Объем двигателя'] = data['Двигатель'].split(" ")[0]
            data['Тип впуска'] = data['Двигатель'].split(" ")[1]
            del data['Двигатель']
            temp = data['Тип топлива']
            data['Тип топлива'] = temp.split(" ")[0]
            data['Рекомендуемое топливо'] = " ".join(temp.split(" ")[1:])
            data['КПП'] = data['Коробка передач'].split(" ")[0]
            data['Количество передач КПП '] = "".join(get_numbers(data['Коробка передач']))
            del data['Коробка передач']
            data['Длина кузова (мм)'] = data['Габариты (длина/ширина/высота), мм'].split(" / ")[0]
            data['Ширина кузова (мм)'] = data['Габариты (длина/ширина/высота), мм'].split(" / ")[1]
            data['Высота кузова (мм)'] = data['Габариты (длина/ширина/высота), мм'].split(" / ")[2]
            del data['Габариты (длина/ширина/высота), мм']

            keys_strong = ['Экстерьер', 'Безопасность', 'Комфорт', 'Адаптация для России']
            for key in keys_strong:
                data[key] = ""

            try:
                keys = response.css(".info-sections > section:nth-child(1) > div > div > div > div > div > div:nth-child(1)::text").extract()
                for id,key in enumerate(keys):
                    keys[id] = key.strip()
                keys = list(filter(None, keys))
                # print(keys)
            except Exception:
                keys = []

            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            values = response.css(".info-sections > section:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(" + str(id + 1) + ") > ul > li > div:nth-child(1)::text").extract()
                            for value in values:
                                data[key1] += value.strip() + "\n"
                            # data[key1] = data[key1][:-len("\n")]
                        except Exception:
                            data[key1] = ""


            keys_strong = ['Пакет "Теплые опции"', 'Экстерьер', 'Интерьер', 'Безопасность', 'Комфорт', 'Мультимедиа']
            for key in keys_strong:
                if key not in data:
                    data[key] = ""

            try:
                keys = response.css(".info-sections > section:nth-child(2) > div > div > div > div > div > div:nth-child(1)::text").extract()
                for id,key in enumerate(keys):
                    keys[id] = key.strip()
                keys = list(filter(None, keys))
                # print(keys)
            except Exception:
                keys = []

            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            values = response.css(".info-sections > section:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(" + str(id + 1) + ") > ul > li > div:nth-child(1)::text").extract()
                            for value in values:
                                data[key1] += value.strip() + "\n"
                            data[key1] = data[key1][:-len("\n")]
                        except Exception:
                            data[key1] = ""

            try:
                data['Фото'] = ""
                photos = response.css(".catalog__detail__content > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div > figure > img:nth-child(1)::attr(data-src)").extract()
                photos = set(photos)
                for photo in photos:
                    data['Фото'] += photo.replace(" ",  "%20") + ","
                data['Фото'] = data['Фото'][:-1]
            except Exception:
                data['Фото'] = ""

            data['Марка'] = "Kia"
            data['Модель'] = response.css("li.text-s3:nth-child(3) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
            data['Комплектация'] = response.css("div.desktop\\:block:nth-child(2)::text").extract_first().strip()

            data['Стоимость'] = "".join(get_numbers(response.css(".catalog-detail-summary__price > div:nth-child(1)::text").extract_first()))
            data['Кредит руб/мес'] = "".join(get_numbers(response.css(".catalog-detail-summary__price > div:nth-child(2)::text").extract_first()))
            
            data["Цвет кузова"] = ""
            data["Номер краски"] = ""
            data["Цвет салона"] = ""
            data["Обивка сидений"] = ""
            keys = response.css("div.catalog-detail-summary__box:nth-child(2) > dl > dt:nth-child(1)::text").extract()
            values = response.css("div.catalog-detail-summary__box:nth-child(2) > dl > dd:nth-child(2)::text").extract()
            for id,key in enumerate(keys):
                key = key.strip()
                value = values[id].strip()
                if key == "Экстерьер":
                    data["Цвет кузова"] = value[0:value.find("(") - 1]
                    data["Номер краски"] =  value[value.find("(")+1:value.find(")")]
                if key == "Интерьер":
                    data["Цвет салона"] = value.split(",")[0]
                    data["Обивка сидений"] = ",".join(value.split(",")[1:]).strip()
            yield data
            


            