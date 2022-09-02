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

token = '8la9INTXeCV9qRoL'
class ToyotaMajorSpider(scrapy.Spider):
    name = 'toyota-major'
    allowed_domains = ['locator-backend.tradedealer.ru', 'toyota-major.ru']
    start_urls = ["https://toyota-major.ru/new-cars/new"]
    

    def parse(self, response):
        # production
        params = (
            ('brands[]', 'toyota'),
            ('order', 'actual'),
            ('page', '1'),
            ('carType', 'new'),
            ('_token', str(token)),
        )
        yield scrapy.FormRequest('https://locator-backend.tradedealer.ru/filter', callback=self.parse_models,
                                     method='GET', formdata=params)

        # # test
        # params = (
        #     ('_token', token),
        # )
        # yield scrapy.FormRequest('https://locator-backend.tradedealer.ru/car/n2475304', callback=self.parse_car,
        #                              method='GET', formdata=params)

    def parse_models(self, response):
        jsonresponse = json.loads(response.text)
        models = jsonresponse['list']
        for model in models:
            pages = math.ceil(model['count'] / 10)
            for page in range(1,pages + 1):
                params = (
                    ('brands[]', 'toyota'),
                    ('models[]', str(model['alias'])),
                    ('order', 'actual'),
                    ('page', str(page)),
                    ('carType', 'new'),
                    ('_token', str(token)),
                )
                yield scrapy.FormRequest('https://locator-backend.tradedealer.ru/filter', callback=self.parse_cars,
                                     method='GET', formdata=params)

    def parse_cars(self, response):
        jsonresponse = json.loads(response.text)
        cars = jsonresponse['list']
        for car in cars:
            params = (
                ('_token', str(token)),
            )
            yield scrapy.FormRequest('https://locator-backend.tradedealer.ru/car/' + str(car['id']), callback=self.parse_car,
                                     method='GET', formdata=params)

    def parse_car(self, response):
        car = json.loads(response.text)
        data = {}

        data['url'] = ""

        try:
            data['Фото'] = ""
            for photo in car['photos']:
                data['Фото'] += photo + ","
            data['Фото'] = data['Фото'][:-1]
        except Exception:
            data['Фото'] = ""

        try:
            data['Видео'] = ""
            for video in car['modelVideos']:
                data['Видео'] += video['link'] + ","
            data['Видео'] = data['Видео'][:-1]
        except Exception:
            data['Видео'] = ""

        try:
            data['Фото модели'] = ""
            for photo in car['modelGalleryImages']:
                data['Фото модели'] += photo + ","
            data['Фото модели'] = data['Фото модели'][:-1]
        except Exception:
            data['Фото модели'] = ""

        if car['status'] == 'stock':
            data['В наличии'] = "В наличии"
        elif car['status'] == 'income':
            data['В наличии'] = "В пути"
        elif car['status'] == 'central_stock':
            data['В наличии'] = "На центральном складе"
        else:
            data['В наличии'] = "Нет в наличии"

        data['Цена'] = car['price']

        data['Цвет'] = car['color']['title']
        data['Год выпуска'] = car['year']
        data['Кузов'] = car['modification']['body']['typeTitle']
        data['Количество мест'] = car['modification']['additional']['seats']
        data['Объем двигателя (л)'] = float(car['modification']['engine']['volume'])
        data['Мощность двигателя (л.с.)'] = car['modification']['engine']['power']
        data['Длина кузова (мм)'] = car['modification']['additional']['length']
        data['Ширина кузова (мм)'] = car['modification']['additional']['width']
        data['Высота кузова (мм)'] = car['modification']['additional']['height']
        data['Объем багажника (л)'] = car['modification']['additional']['trunkVolume']
        data['Рекомендуемое топливо'] = car['modification']['engine']['fuel']['title']
        data['Емкость топливного бака'] = car['modification']['additional']['fuelTank']
        data['Смешанный цикл (на 100км)'] = car['modification']['additional']['fuelConsumptionComb']
        data['Городской цикл (на 100км)'] = car['modification']['additional']['fuelConsumptionCity']
        data['Загородный цикл (на 100км)'] = car['modification']['additional']['fuelConsumptionRoad']
        data['Максимальная скорость'] = car['modification']['additional']['maxVelocity']
        data['Время разгона 0-100 км/ч'] = car['modification']['additional']['timeTo100kph']

        data['Экстерьер'] = ""
        data['Комфорт'] = ""
        data['Безопасность'] = ""
        data['Мультимедиа'] = ""
        data['Противоугонные системы'] = ""
        data['Зимний комфорт'] = ""
        data['Пассивная безопасность'] = ""
        for option in car['complectation']['optionGroups']:
            if option['title'] == 'Экстерьер':
                for elem in option['options']:
                    data['Экстерьер'] += elem['title'] + ","
                data['Экстерьер'] = data['Экстерьер'][:-1]

            if option['title'] == 'Комфорт':
                for elem in option['options']:
                    data['Комфорт'] += elem['title'] + ","
                data['Комфорт'] = data['Комфорт'][:-1]

            if option['title'] == 'Безопасность':
                for elem in option['options']:
                    data['Безопасность'] += elem['title'] + ","
                data['Безопасность'] = data['Безопасность'][:-1]

            if option['title'] == 'Мультимедиа':
                for elem in option['options']:
                    data['Мультимедиа'] += elem['title'] + ","
                data['Мультимедиа'] = data['Мультимедиа'][:-1]

            if option['title'] == 'Противоугонные системы':
                for elem in option['options']:
                    data['Противоугонные системы'] += elem['title'] + ","
                data['Противоугонные системы'] = data['Противоугонные системы'][:-1]

            if option['title'] == 'Зимний комфорт':
                for elem in option['options']:
                    data['Зимний комфорт'] += elem['title'] + ","
                data['Зимний комфорт'] = data['Зимний комфорт'][:-1]

            if option['title'] == 'Пассивная безопасность':
                for elem in option['options']:
                    data['Пассивная безопасность'] += elem['title'] + ","
                data['Пассивная безопасность'] = data['Пассивная безопасность'][:-1]

        data['Дополнительное оборудование + цена'] = ""
        for add in car['addEquipment']:
            data['Дополнительное оборудование + цена'] += str(add['price']) + "<section>" + add['name'] + "<separator>"

        data['Марка'] = car['brand']['title']
        data['Модель'] = car['model']['title']
        data['Комплектация'] = car['complectation']['title']

        if car['modification']['drivetrain'] == "fwd":
            data['Привод'] = "Передний"
        elif car['modification']['drivetrain'] == "4wd":
            data['Привод'] = "Полный"
        else:
            data['Привод'] = ""

        data['Адрес салона'] = car['company']['city']['title'] + ", " + car['company']['address']

        data['Юридическая информация'] = ""
        data['Юридическая информация'] += "В комплектациях с кожаной обивкой салона применяется комбинация из натуральной и синтетической кожи.\n"
        data['Юридическая информация'] += "Автомобили, представленные на фото, могут отличаться от автомобилей, доступных для заказа у официальных дилеров Тойота.\n"
        data['Юридическая информация'] += "Автомобиль поступит в дилерский центр в срок от 1 до 40 дней. Точную дату доставки вы можете уточнить у сотрудника дилерского центра.\n"
        data['Юридическая информация'] += "Автомобиль поступит в дилерский центр в срок от 7 до 150 дней. Точную дату доставки вы можете уточнить у сотрудника дилерского центра.\n"
        data['Юридическая информация'] += "Цены, указанные на сайте, идут без учета дополнительно установленных аксессуаров. Наличие аксессуаров на выбранном авто, стоимость автомобиля вы можете уточнить у сотрудника дилерского центра.\n"

        data['url'] = "https://toyota-major.ru/new-cars/new/" + car['brand']['alias'] + "/" + car['model']['alias'] + "/" + car['id'] 

        yield data




