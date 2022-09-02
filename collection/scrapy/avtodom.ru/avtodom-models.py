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

class AvtodomModelsSpider(scrapy.Spider):
    name = 'avtodom-models'
    allowed_domains = ['avtodom.ru']
    start_urls = ["https://avtodom.ru/allcars/?PAGEN_1=1"]

    def parse(self, response):
        # test
        # yield Request("https://avtodom.ru/catalog/jaguar/xf/", callback=self.parse_models, dont_filter=True) 
        # yield Request("https://avtodom.ru/catalog/audi/a3-sedan/", callback=self.parse_models, dont_filter=True) 

        # production
        pages = response.css(".-columns > li > a:nth-child(1)::attr(href)").extract()
        for page in pages:
            yield Request("https://avtodom.ru" + page, callback=self.parse_page)

    def parse_page(self, response):
        links = response.css("div.catalog__model > a:nth-child(1)::attr(href)").extract()
        for link in links:
            link = "https://avtodom.ru" + link
            # print(link)
            yield Request(link, callback=self.parse_models, dont_filter=True)     

    def parse_models(self, response):
        data = {}
        data['url'] = response.request.url
        data['Марка'] = response.css("li.breadcrumbs__item:nth-child(3) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
        data['Модель'] = response.css("li.breadcrumbs__item:nth-child(4) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
        for response in response.css("body"):
            models = response.css("li.product-tabs__item > a:nth-child(1) > span:nth-child(1)::text").extract()
            for model in models:
                data['Комплектация'] = model.strip()
                # models = response.css("li.product-tabs__item > a:nth-child(1) > span:nth-child(1)::text").extract()
                for id,mod in enumerate(models):
                    if mod.strip() == model.strip():
                        values = response.css("#product-tab-" + str(id+1) + " div.product-description__item-value > span:nth-child(1)::text").extract()
                        keys   = response.css("#product-tab-" + str(id+1) + " div.product-description__item-name > span:nth-child(1)::text").extract()
                # print(values)
                keys_strong = ['Номинальная мощность, кВ / об/мин', 'Номинальный крутящий момент, Нм при об/мин', 'Время разгона, с', 
                                'Максимальная скорость, км/ч', 'Объем, л', 'Комбинированный, л/100 км', 
                                'Время зарядки, ч', 'Подзарядка на дому', 'Снаряженная масса, кг', 'Полная нормативная масса, кг',
                                'Колесная база, мм', 'Ширина, включая зеркала, мм', 
                                'Максимальная высота над передними/задними сиденьями со стандартной крышей, мм', 
                                'Максимальная высота над передними/задними сиденьями с панорамной крышей, мм', 
                                'Максимальное пространство для ног в передней/задней части салона, мм', 
                                'Ширина между колесными арками, мм', 'Длина за сиденьями первого ряда, мм', 'Стандартная высота подвески, мм',
                                'Прицеп, не оснащенный тормозной системой', 'Максимальная масса буксируемого груза, кг',
                                'Максимальная вертикальная нагрузка на точку сцепки (крюк), кг', 'Максимальная масса автомобиля с прицепом (GTW), кг']
                for key in keys_strong:
                    data[key] = ""

                try:
                    for id,key in enumerate(keys):
                        keys[id] = key.strip()
                    keys = list(filter(None, keys))
                except Exception:
                    keys = []

                for id,key in enumerate(keys):
                    for key1 in keys_strong:
                        if (key == key1):
                            try:
                                if key1 == "Номинальная мощность, кВ / об/мин":
                                    val = values[id].strip()
                                    data['Максимальная мощность'] = val.split("/")[0]
                                    data['Обороты максимальной мощности'] = val.split("/")[1]
                                    del data['Номинальная мощность, кВ / об/мин']
                                elif key1 == 'Номинальный крутящий момент, Нм при об/мин':
                                    val = values[id].strip()
                                    data['Максимальный крутящий момент'] = val.split('/')[0].strip()
                                    data['Обороты максимального крутящего момента'] = val.split('-')[1].strip()
                                    del data['Номинальный крутящий момент, Нм при об/мин']
                                else:
                                    data[key1] = values[id].strip()
                            except Exception:
                                data[key1] = ""

                try:
                    data['О модели'] = response.css(".product-gallery__text-full > p:nth-child(1)::text").extract_first().strip()
                except Exception:
                    data['О модели'] = ""

                
                try:
                    data['Адреса дилеров'] = ""
                    adresses = response.css("div.dealers-slider__text::text").extract()
                    adresses = set(adresses)
                    for adress in adresses:
                        data['Адреса дилеров'] += adress.strip() + ";"
                    data['Адреса дилеров'] = data['Адреса дилеров'][:-1]
                except Exception:
                    data['Адреса дилеров'] = ""
                colors = response.css("li.product-colors__item > button:nth-child(1)::attr(style)").extract()
                data_ids = response.css("li.product-colors__item > button:nth-child(1)::attr(data-index)").extract()
                if colors:
                    for id,color in enumerate(colors):
                        color = color[color.find("#"):color.find(";")]
                        data['Цвет'] = color
                        data_id = data_ids[id]
                        photos = response.css("img.product-images__image::attr(src)").extract()
                        photos_ids = response.css("img.product-images__image::attr(data-index)").extract()
                        for id,photo in enumerate(photos):
                            if photos_ids[id] == data_id:
                                data['Фото'] = "https://avtodom.ru" + photo
                        yield data   
                else:
                    data['Фото'] = "https://avtodom.ru" + response.css("img.product-images__image::attr(src)").extract_first()
                    yield data

    # def parse_models(self, response):
    #     data = {}
    #     data['url'] = response.request.url
    #     data['Марка'] = response.css("li.breadcrumbs__item:nth-child(3) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
    #     data['Модель'] = response.css("li.breadcrumbs__item:nth-child(4) > a:nth-child(1) > span:nth-child(1)::text").extract_first()
    #     for response in response.css("body"):
    #         models = response.css("li.product-tabs__item > a:nth-child(1) > span:nth-child(1)::text").extract()
    #         for model in models:
    #             yield Request(data['url'], callback=self.parse_model, meta={'model':model, 'data':data}, dont_filter=True)

    # def parse_model(self, response):
    #     model = response.meta['model'].strip()
    #     data = response.meta['data']
    #     data['Комплектация'] = model

    #     models = response.css("li.product-tabs__item > a:nth-child(1) > span:nth-child(1)::text").extract()
    #     for id,mod in enumerate(models):
    #         if mod.strip() == model:
    #             values = response.css("#product-tab-" + str(id+1) + " div.product-description__item-value > span:nth-child(1)::text").extract()
    #             keys   = response.css("#product-tab-" + str(id+1) + " div.product-description__item-name > span:nth-child(1)::text").extract()

    #     keys_strong = ['Номинальная мощность, кВ / об/мин', 'Номинальный крутящий момент, Нм при об/мин', 'Время разгона, с', 
    #                     'Максимальная скорость, км/ч', 'Объем, л', 'Комбинированный, л/100 км', 
    #                     'Время зарядки, ч', 'Подзарядка на дому', 'Снаряженная масса, кг', 'Полная нормативная масса, кг',
    #                     'Колесная база, мм', 'Ширина, включая зеркала, мм', 
    #                     'Максимальная высота над передними/задними сиденьями со стандартной крышей, мм', 
    #                     'Максимальная высота над передними/задними сиденьями с панорамной крышей, мм', 
    #                     'Максимальное пространство для ног в передней/задней части салона, мм', 
    #                     'Ширина между колесными арками, мм', 'Длина за сиденьями первого ряда, мм', 'Стандартная высота подвески, мм',
    #                     'Прицеп, не оснащенный тормозной системой', 'Максимальная масса буксируемого груза, кг',
    #                     'Максимальная вертикальная нагрузка на точку сцепки (крюк), кг', 'Максимальная масса автомобиля с прицепом (GTW), кг']
    #     for key in keys_strong:
    #         data[key] = ""

    #     try:
    #         for id,key in enumerate(keys):
    #             keys[id] = key.strip()
    #         keys = list(filter(None, keys))
    #     except Exception:
    #         keys = []

    #     for id,key in enumerate(keys):
    #         for key1 in keys_strong:
    #             if (key == key1):
    #                 try:
    #                     if key1 == "Номинальная мощность, кВ / об/мин":
    #                         val = values[id].strip()
    #                         data['Максимальная мощность'] = val.split("/")[0]
    #                         data['Обороты максимальной мощности'] = val.split("/")[1]
    #                         del data['Номинальная мощность, кВ / об/мин']
    #                     elif key1 == 'Номинальный крутящий момент, Нм при об/мин':
    #                         val = values[id].strip()
    #                         data['Максимальный крутящий момент'] = val.split('/')[0].strip()
    #                         data['Обороты максимального крутящего момента'] = val.split('-')[1].strip()
    #                         del data['Номинальный крутящий момент, Нм при об/мин']
    #                     else:
    #                         data[key1] = values[id].strip()
    #                 except Exception:
    #                     data[key1] = ""

    #     try:
    #         data['О модели'] = response.css(".product-gallery__text-full > p:nth-child(1)::text").extract_first().strip()
    #     except Exception:
    #         data['О модели'] = ""

        
    #     try:
    #         data['Адреса дилеров'] = ""
    #         adresses = response.css("div.dealers-slider__text::text").extract()
    #         adresses = set(adresses)
    #         for adress in adresses:
    #             data['Адреса дилеров'] += adress.strip() + ";"
    #         data['Адреса дилеров'] = data['Адреса дилеров'][:-1]
    #     except Exception:
    #         data['Адреса дилеров'] = ""

    #     colors = response.css("li.product-colors__item > button:nth-child(1)::attr(style)").extract()
    #     data_ids = response.css("li.product-colors__item > button:nth-child(1)::attr(data-index)").extract()
    #     for id,color in enumerate(colors):
    #         color = color[color.find("#"):color.find(";")]
    #         yield Request(data['url'], callback=self.parse_color, meta={'color':color, 'data_id':data_ids[id], 'data':data}, dont_filter=True)

    # def parse_color(self, response):
    #     color = response.meta['color'].strip()
    #     data_id = response.meta['data_id'].strip()
    #     data = response.meta['data']
    #     data['Цвет'] = color
    #     photos = response.css("img.product-images__image::attr(src)").extract()
    #     photos_ids = response.css("img.product-images__image::attr(data-index)").extract()
    #     for id,photo in enumerate(photos):
    #         if photos_ids[id] == data_id:
    #             data['Фото'] = "https://avtodom.ru" + photo
    #     yield data











