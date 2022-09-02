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

class MajorAutoSpider(scrapy.Spider):
    name = 'major-auto'
    allowed_domains = ['www.major-auto.ru']
    start_urls = ["https://www.major-auto.ru/cars/brands/"]

    def parse(self, response):
        models_count = "".join(get_numbers(response.css("head > meta[name=\"description\"]::attr(content)").extract_first()))
        count = math.ceil(int(models_count) / 6)

        # test
        # count = 1

        for i in range(1, int(count)+1):
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
            }

            data = {
              'page': str(i)
            }

            yield scrapy.FormRequest('https://www.major-auto.ru/ajax/carsexpert/getCarsListGrouped/?ajax_display_mode', headers=headers, callback=self.parse_link,
                                     method='POST', formdata=data)

    def parse_link(self, response):
        for response in response.css("body"):
            html = response.extract()
            key = "<a href=\\\""
            count = html.count(key)
            links = []
            for i in range(0, count):
                first = html.find(key)
                last = html.find("\"", first + len(key) + 1)
                link = html[first + len(key):last]
                if (link.find("car") != -1 and link.find("page") == -1):
                    link = "https://www.major-auto.ru" + link.replace("\\", "")
                    links.append(link)
                html = html[first + len(key) + 1:]
            for link in links:
                yield Request(link, callback=self.parse_car)
                # pass
            # yield Request("https://www.major-auto.ru/cars/brands/chery/txl/1392693/", callback=self.parse_car)
            # yield Request("https://www.major-auto.ru/cars/brands/mazda/cx-5_ii/1028449/", callback=self.parse_car)
            

    def parse_car(self, response):
        data = {}
        data['url'] = response.request.url
        for response in response.css("body"):
            # data = {}
            try:
                data['Видео'] = ""
                videos = response.css("div.visual_blocks > div.youtube_video > div::attr(data-link)").extract()
                for link in videos:
                    data['Видео'] += link.replace(" ",  "%20") + "," 
                data['Видео'] = data['Видео'][:-1]
            except Exception:
                data['Видео'] = ""

            try:
                data['Фото'] = ""
                photos = response.css("div.gallery-item > img::attr(src)").extract()
                photos = set(photos)
                for photo in photos:
                    data['Фото'] += "https://www.major-auto.ru" + photo.replace(" ",  "%20") + ","
                data['Фото'] = data['Фото'][:-1]
            except Exception:
                data['Фото'] = ""

            if data['Фото'] == "":
                data['Фото'] = response.css("img::attr(src)").extract()[-1].replace(" ",  "%20")

            try:
                data['Цена при резерве онлайн'] = "".join(get_numbers(response.css("div.d-md-block:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(3)::text").extract_first()))
            except Exception:
                data['Цена при резерве онлайн'] = ""

            try:
                data['Минимальная цена'] = "".join(get_numbers(response.css("div.d-md-block:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2)::text").extract_first()))
            except Exception:
                data['Минимальная цена'] = ""

            keys_strong = ["Экстерьер", "Интерьер", "Комфорт", "Безопасность", "Мультимедийные системы и связь", "Противоугонные системы", "Общее"]
            for key in keys_strong:
                data[key] = ""

            try:
                cats = response.css("div.d-xl-block div.tab_panel_all > ul > li > div.options_group_title::text").extract()
                for id,cat in enumerate(cats):
                    cats[id] = cat.strip()
                cats = list(filter(None, cats))
            except Exception:
                cats = []

            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            values = response.css("div.d-none:nth-child(4) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(" + str(id + 1) + ") > ul:nth-child(2) > li > div:nth-child(1)::text").extract()
                            for value in values:
                                data[key1] += value.strip() + "<section>"
                            data[key1] = data[key1][:-len("<section>")]
                        except Exception:
                            data[key1] = ""

            keys_strong = ['Тип двигателя', 'Объем двигателя, л', 'Мощность двигателя, л.с.', 'Максимальный крутящий момент, Н•м', 'Загородный расход, л/100 км', 'Городской расход, л/100 км', 'Смешанный расход, л/100 км', 'Время разгона до 100 км/ч, с', 'Тип КПП', 'Количество передач КПП', 'Тип Привода', 'Тип кузова', 'Количество дверей', 'Объем багажника, л', 'Длина, мм', 'Ширина, мм', 'Высота, мм', 'Дорожный просвет (клиренс), мм', 'Гарантия']
            for key in keys_strong:
                data[key] = ""

            try:
                cats = response.css("div.d-xl-block span.tth_param_name::text").extract()
                for id,cat in enumerate(cats):
                    cats[id] = cat.strip()
                cats = list(filter(None, cats))
            except Exception:
                cats = []

            values = response.css("div.d-xl-block span.tth_param_value::text").extract()
            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""

            keys_strong = ['Цвет', 'Кузов', 'Класс', 'Салон']
            for key in keys_strong:
                data[key] = ""

            try:
                cats = response.css("div.main-description-car div.title::text").extract()
                for id,cat in enumerate(cats):
                    if (cat.strip()[-1] == ":"):
                        cats[id] = cat.strip()[:-1]
                    else:
                        cats[id] = cat.strip()
                cats = list(filter(None, cats))
            except Exception:
                cats = []

            values = response.css("div.main-description-car div.description::text").extract()
            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""

            try:
                data['Адреса салонов'] = ""
                addresses = response.css("div.address::text").extract()
                i = 0
                for address in addresses:
                    if (i == 0):
                        data['Адреса салонов'] += address.strip() + "\n"
                        i = 1
                    else:
                        data['Адреса салонов'] += address.strip() + "<section>"
                        i = 0
                data['Адреса салонов'] = data['Адреса салонов'][:-len("<section>")]
            except Exception:
                data['Адреса салонов'] = ""

            try:
                data['Другие варианты в наличии'] = ""
                links = response.css("div.same-cars a::attr(href)").extract()
                for link in links:
                    data['Другие варианты в наличии'] += "https://www.major-auto.ru" + link.replace(" ",  "%20") + ","
                data['Другие варианты в наличии'] = data['Другие варианты в наличии'][:-len(",")]
            except Exception:
                data['Другие варианты в наличии'] = ""

            try:
                data['Авто с пробегом'] = ""
                links = response.css("a.-used::attr(href)").extract()
                for link in links:
                    data['Авто с пробегом'] += link.replace("//www.major-expert.ru", "https://www.major-auto.ru") + ","
                data['Авто с пробегом'] = data['Авто с пробегом'][:-len(",")]
            except Exception:
                data['Авто с пробегом'] = ""

            try:
                year = response.css("div.caption::text").extract_first()
                data['Год выпуска'] = re.findall(r'\d+', year)[0]
            except Exception:
                data['Год выпуска'] = ""

            try:
                data["Теги"] = ""
                tags = response.css("span.label::text").extract()
                tags = set(tags)
                for tag in tags:
                    data["Теги"] += tag + ","
                data["Теги"] = data["Теги"][0:-1]
            except Exception:
                data["Теги"] = ""

            try:
                data["Автосалон где купить"] = ""
                links = response.css("a.block-car-salon::attr(href)").extract()
                links = set(links)
                for link in links:
                    data["Автосалон где купить"] += "https://www.major-auto.ru" + link + ","
                data["Автосалон где купить"] = data["Автосалон где купить"][0:-1]
            except Exception:
                data["Автосалон где купить"] = ""

            try:
                data['Доступные цвета'] = ""
                colors_hints = response.css("a.color::attr(title)").extract()
                colors_links = response.css("a.color::attr(href)").extract()
                colors_hexs  = response.css("a.color::attr(style)").extract()
                for id,color in enumerate(colors_hints):
                    colors_hexs[id] = colors_hexs[id].split("background:", 1)[1]
                    colors_hexs[id] = colors_hexs[id].split(";", 1)[0]
                    colors_links[id] = "https://www.major-auto.ru" + colors_links[id]
                    data['Доступные цвета'] += colors_hints[id] + "<section>" + colors_hexs[id] + "<section>" + colors_links[id] + ","
                data['Доступные цвета'] = data['Доступные цвета'][0:-1]
            except Exception:
                data['Доступные цвета'] = ""
            
            keys_strong = ['Trade-In', 'Кредит минимальная цена', 'Выгода']
            for key in keys_strong:
                data[key] = ""

            try:
                try:
                    cats = response.css("div.col-xl-4 div.option_title::text").extract()
                    for id,cat in enumerate(cats):
                        if (cat.strip()[-1] == ":"):
                            cats[id] = cat.strip()[:-1]
                        else:
                            cats[id] = cat.strip()
                    cats = list(filter(None, cats))
                except Exception:
                    cats = []

                try:
                    values = response.css("div.col-xl-4 span.option_value::text").extract()
                    for id,value in enumerate(values):
                        values[id] = value.strip()
                    values = list(filter(None, values))
                except Exception:
                    values = []

                for id,key in enumerate(cats):
                    for key1 in keys_strong:
                        if (key == key1):
                            try:
                                if   (key == "Trade-In"):
                                    data[key1] = "".join(get_numbers(values[id].strip()))
                                elif (key == "Выгода"):
                                    data[key1] = "".join(get_numbers(values[id].strip())) 
                                else:
                                    data[key1] = values[id].strip()
                            except Exception:
                                data[key1] = ""
            except Exception:
                pass

            try:
                city = response.css("div.col-xl-4 span.geo-instock-text::text").extract_first().strip()
                data['В наличии в городе'] = city.replace("В наличии в ", "")
            except Exception:
                data['В наличии в городе'] = ""

            try:
                data['Марка'] = response.css("a.link:nth-child(7)::text").extract_first()
            except Exception:
                data['Марка'] = ""

            try:
                data['Модель'] = response.css("a.link:nth-child(9)::text").extract_first()
            except Exception:
                data['Модель'] = ""

            try:
                temp = response.css(".page-content > div > h1::text").extract_first()
                temp = temp.replace(data['Марка'], "")
                words = data['Модель'].split(" ")
                for word in words:
                    temp = temp.replace(word, "")
                data['Комплектация'] = temp.strip()
            except Exception:
                data['Комлпектация'] = ""

            yield data
            


            