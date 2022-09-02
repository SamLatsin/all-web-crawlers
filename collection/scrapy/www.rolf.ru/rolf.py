import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())

class RolfSpider(scrapy.Spider):
    name = 'rolf'
    allowed_domains = ['www.rolf.ru']
    # start_urls = ["https://www.rolf.ru/cars/new/nissan/qashqai/stock_car524171/"]
    start_urls = ["https://www.rolf.ru/cars/new/nissan/qashqai/stock_car524171/"]

    # def start_requests(self):
    #     with open("./../links input/creditznatok-input.csv", encoding = 'utf-8') as f:
    #         start_urls = [url.strip() for url in f.readlines()]
    #         start_urls = start_urls[1:]
    #         for url in start_urls:
    #             yield Request(url)

    def parse(self, response):
        data = {}
        data['url'] = response.request.url
        for response in response.css("body"):
            # data = {}
            try:
                data['Специальная цена'] = "".join(response.css("div.car-page__price-block:nth-child(1) > p:nth-child(2) > span:nth-child(1)::text").extract_first().split(" "))
            except Exception:
                data['Специальная цена'] = ""
            
            try:
                data['Стоимость автомобиля'] = "".join(response.css("div.car-page__price-block:nth-child(2) > p:nth-child(2)::text").extract_first().split(" "))
            except Exception:
                data['Стоимость автомобиля'] = ""

            # правое меню
            data['Компенсация Trade-in'] = ""
            data['Скидка при оформлении КАСКО'] = ""
            data['Скидка при покупке в кредит'] = ""
            keys =   response.css("div.car-page__discount-item-wrapper > div > label > span:nth-child(2)::text").extract()
            values = response.css("div.car-page__discount-item-wrapper > div > label > span:nth-child(3)::text").extract()
            for id, value in enumerate(keys):
                value = re.sub(' +', ' ', value.strip())
                if (value.find("Компенсация") != -1 ):
                    data['Компенсация Trade-in'] = "".join(re.findall(r'\d+', values[id]))
                if (value.strip().find("Скидка при оформлении") != -1 ):
                    data['Скидка при оформлении КАСКО'] = "".join(re.findall(r'\d+', values[id+1]))
                if (value.strip().find("Скидка при покупке") != -1 ):
                    data['Скидка при покупке в кредит'] = "".join(re.findall(r'\d+', values[id+2]))

            try:
                data['Максимальная скидка'] = response.css("div.car-page__discount-item-row:nth-child(2) > p:nth-child(2)::text").extract_first()
                data['Максимальная скидка'] = "".join(re.findall(r'\d+', data['Максимальная скидка']))
            except Exception:
                data['Максимальная скидка'] = ""

            try:
                data['Кредит'] = response.css("div.car-page__discount-item-row:nth-child(3) > p:nth-child(2)::text").extract_first().strip()
            except Exception:
                data['Кредит'] = ""

            try:
                imgs = response.css(".gallery__list img::attr(data-image-preload)").extract()
                for id, value in enumerate(imgs):
                    imgs[id] = "https://www.rolf.ru" + imgs[id]
                data['imgs'] = ",".join(imgs)
            except Exception:
                data['imgs'] = ""

            # Парсинг таблицы
            data['Комплектация'] = ""
            data['Год выпуска'] = ""
            data['Тип кузова'] = ""
            data['КПП'] = ""
            data['Мощность двигателя'] = ""
            data['Объем двигателя'] = ""
            data['Двигатель'] = ""
            data['Привод'] = ""
            data['Цвет кузова'] = ""
            data['Тип усилителя'] = ""

            data['Тип двигателя'] = ""
            data['Количество цилиндров'] = ""
            data['Количество клапанов на цилиндр'] = ""
            data['Рабочий объем'] = ""
            data['Конфигурация'] = ""
            data['Максимальная мощность'] = ""
            data['Обороты максимальной мощности'] = ""
            data['Максимальный крутящий момент'] = ""
            data['Обороты максимального крутящего момента'] = ""
            data['Тип впуска'] = ""

            data['Количество мест'] = ""
            data['Длина кузова'] = ""
            data['Ширина кузова'] = ""
            data['Высота кузова'] = ""
            data['Колесная база'] = ""
            data['Колея передних колес'] = ""
            data['Колея задних колес'] = ""
            data['Дорожный просвет'] = ""
            data['Диаметр разворота'] = ""
            data['Снаряженная масса'] = ""
            data['Полная масса'] = ""

            data['Максимальная скорость'] = ""
            data['Время разгона 0-100 км/ч'] = ""
            data['Смешанный цикл'] = ""
            data['Городской цикл'] = ""
            data['Загородный цикл'] = ""
            data['Рекомендуемое топливо'] = ""
            data['Емкость топливного бака'] = ""
            data['Соответствие экологическим требованиям'] = ""

            data['Передняя подвеска'] = ""
            data['Задняя подвеска'] = ""
            data['Передние тормоза'] = ""
            data['Задние тормоза'] = ""

            data['Передние шины'] = ""
            data['Задние шины'] = ""
            data['Передние диски'] = ""
            data['Задние диски'] = ""

            data['Страна производства'] = ""

            keys = response.css("div.accordion__group-item-key::text").extract()
            values = response.css("div.accordion__group-item-value::text").extract()
            for id, value in enumerate(keys):
                value = re.sub(' +', ' ', value.strip())
                if (value.find("Комплектация") != -1 ):
                    data['Комплектация'] = values[id]
                if (value.find("Год выпуска") != -1 ):
                    data['Год выпуска'] = values[id]
                if (value.find("Кузов") != -1 ):
                    data['Тип кузова'] = values[id]
                if (value.find("КПП") != -1 ):
                    data['КПП'] = values[id]
                if (value.find("Мощность") != -1 ):
                    data['Мощность двигателя'] = values[id]
                if (value.find("Объем двигателя") != -1 ):
                    data['Объем двигателя'] = values[id]
                if (value.find("Двигатель") != -1 ):
                    data['Двигатель'] = values[id]
                if (value.find("Привод") != -1 ):
                    data['Привод'] = values[id]
                if (value.find("Цвет кузова") != -1 ):
                    data['Цвет кузова'] = values[id]
                if (value.find("Тип усилителя") != -1 ):
                    data['Тип усилителя'] = values[id]

                if (value.find("Тип двигателя") != -1 ):
                    data['Тип двигателя'] = values[id]
                if (value.find("Количество цилиндров") != -1 ):
                    data['Количество цилиндров'] = values[id]
                if (value.find("Количество клапанов на цилиндр") != -1 ):
                    data['Количество клапанов на цилиндр'] = values[id]
                if (value.find("Рабочий объем") != -1 ):
                    data['Рабочий объем'] = values[id]
                if (value.find("Конфигурация") != -1 ):
                    data['Конфигурация'] = values[id]
                if (value.find("Максимальная мощность") != -1 ):
                    data['Максимальная мощность'] = values[id]
                if (value.find("Обороты максимальной мощности") != -1 ):
                    data['Обороты максимальной мощности'] = values[id]
                if (value.find("Максимальный крутящий момент") != -1 ):
                    data['Максимальный крутящий момент'] = values[id]
                if (value.find("Обороты максимального крутящего момента") != -1 ):
                    data['Обороты максимального крутящего момента'] = values[id]
                if (value.find("Тип впуска") != -1 ):
                    data['Тип впуска'] = values[id]

                if (value.find("Количество мест") != -1 ):
                    data['Количество мест'] = values[id]
                if (value.find("Длина") != -1 ):
                    data['Длина кузова'] = values[id]
                if (value.find("Ширина") != -1 ):
                    data['Ширина кузова'] = values[id]
                if (value.find("Высота") != -1 ):
                    data['Высота кузова'] = values[id]
                if (value.find("Колесная база") != -1 ):
                    data['Колесная база'] = values[id]
                if (value.find("Колея передних колес") != -1 ):
                    data['Колея передних колес'] = values[id]
                if (value.find("Колея задних колес") != -1 ):
                    data['Колея задних колес'] = values[id]
                if (value.find("Дорожный просвет") != -1 ):
                    data['Дорожный просвет'] = values[id]
                if (value.find("Диаметр разворота") != -1 ):
                    data['Диаметр разворота'] = values[id]
                if (value.find("Снаряженная масса") != -1 ):
                    data['Снаряженная масса'] = values[id]
                if (value.find("Полная масса") != -1 ):
                    data['Полная масса'] = values[id]

                if (value.find("Максимальная скорость") != -1 ):
                    data['Максимальная скорость'] = values[id]
                if (value.find("Время разгона") != -1 ):
                    data['Время разгона 0-100 км/ч'] = values[id]
                if (value.find("Смешанный цикл") != -1 ):
                    data['Смешанный цикл'] = values[id]
                if (value.find("Городской цикл") != -1 ):
                    data['Городской цикл'] = values[id]
                if (value.find("Загородный цикл") != -1 ):
                    data['Загородный цикл'] = values[id]
                if (value.find("Рекомендуемое топливо") != -1 ):
                    data['Рекомендуемое топливо'] = values[id]
                if (value.find("Емкость топливного бака") != -1 ):
                    data['Емкость топливного бака'] = values[id]
                if (value.find("Соответствие экологическим требованиям") != -1 ):
                    data['Соответствие экологическим требованиям'] = values[id]

                if (value.find("Передняя подвеска") != -1 ):
                    data['Передняя подвеска'] = values[id]
                if (value.find("Задняя подвеска") != -1 ):
                    data['Задняя подвеска'] = values[id]
                if (value.find("Передние тормоза") != -1 ):
                    data['Передние тормоза'] = values[id]
                if (value.find("Задние тормоза") != -1 ):
                    data['Задние тормоза'] = values[id]

                if (value.find("Передние шины") != -1 ):
                    data['Передние шины'] = values[id]
                if (value.find("Задние шины") != -1 ):
                    data['Задние шины'] = values[id]
                if (value.find("Передние диски") != -1 ):
                    data['Передние диски'] = values[id]
                if (value.find("Задние диски") != -1 ):
                    data['Задние диски'] = values[id]

                if (value.find("Страна производства") != -1 ):
                    data['Страна производства'] = values[id]

            try:
                data["Адрес"] = ""
                data["Адрес"] = response.css("div.car-page__map-block:nth-child(3) > p:nth-child(2)::text").extract_first()
                data["Адрес"] = remove_spaces(data["Адрес"])
                data["Адрес"] = data["Адрес"].replace("\xa0", " ")
            except Exception:
                data["Адрес"] = ""

            try:
                data['Другие варианты в наличии'] = ""
                others = response.css("div.main-block:nth-child(5) > div:nth-child(1) > div:nth-child(2) > a::attr(href)").extract()
                for id, value in enumerate(others):
                    others[id] = "https://www.rolf.ru" + others[id]
                data['Другие варианты в наличии'] = ",".join(others)
            except Exception:
                data['Другие варианты в наличии'] = ""

            try:
                data['Акции'] = ""
                stock = response.css("a.slider-collections__list-item::attr(href)").extract()
                for id, value in enumerate(stock):
                    stock[id] = "https://www.rolf.ru" + stock[id]
                data['Акции'] = ",".join(stock)
            except Exception:
                data['Акции'] = ""

            try:
                data['Марка'] = response.css("div.hide:nth-child(5)::text").extract_first().strip()
            except Exception:
                data['Марка'] = ""
            
            try:
                data['Модель'] = response.css("h2.jc-sb::text").extract_first().strip().replace(data['Марка'], "").strip()
            except Exception:
                data['Модель'] = ""

            data['Экстерьер'] = ""
            data['Комфорт'] = ""
            data['Активная безопасность и подвеска'] = ""
            data['Аудио- и информационно-развлекательные системы'] = ""
            data['Запасное колесо'] = ""
            data['Интерьер'] = ""
            keys = response.css("div[data-tab=\"complectation\"] > div > div > div > div.accordion__group-header > div.accordion__group-name::text").extract()
            for id, value in enumerate(keys):
                value = re.sub(' +', ' ', value.strip())
                if (value.find("Экстерьер") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Экстерьер'] = ",".join(values)
                if (value.find("Комфорт") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Комфорт'] = ",".join(values)
                if (value.find("Активная безопасность и подвеска") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Активная безопасность и подвеска'] = ",".join(values)
                if (value.find("Аудио- и информационно-развлекательные системы") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Аудио- и информационно-развлекательные системы'] = ",".join(values)
                if (value.find("Запасное колесо") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Запасное колесо'] = ",".join(values)
                if (value.find("Интерьер") != -1 ):
                    values = response.css("div[data-tab=\"complectation\"] > div > div > div:nth-child(" + str(id+1) + ") > div.accordion__group-items > div.accordion__group-item::text").extract()
                    for id1, value1 in enumerate(values):
                        values[id1] = re.sub(' +', ' ', values[id1].strip())
                    data['Интерьер'] = ",".join(values)
            yield data

            