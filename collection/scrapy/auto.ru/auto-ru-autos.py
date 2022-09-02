import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
from scrapy.http import HtmlResponse

# from scrapy_splash import SplashRequest
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.action_chains import ActionChains
from shutil import which

token = '636224dafc34b7e0c38f88d0e90b7d6de0789c68d439dfb3'
coords = [38, 76, 18, 165] # Russia coords

cookies = {
    '_csrf_token': token,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0',
    'x-csrf-token': token,
    'content-type': 'application/json',
    'Origin': 'https://auto.ru',
}

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

class AvtodomSpider(scrapy.Spider):
    name = 'avto-ru-autos'
    allowed_domains = ['avto.ru']
    start_urls =["https://auto.ru/dilery/cars/all/"]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        'SELENIUM_DRIVER_NAME' : 'firefox',
        'SELENIUM_DRIVER_EXECUTABLE_PATH' : which('geckodriver'),
        'SELENIUM_DRIVER_ARGUMENTS' : ['-headless', '-disable-gpu', '-silent']
    }

    def parse_dealer_links(self,response):
        coords = response.meta['coords']
        dealers = json.loads(response.text)
        if (dealers['totalResultsCount'] > 300):
            print("more than 300 results (" + str(dealers['totalResultsCount']) + "), dividing...")
            coords1 = [coords[0], (coords[1]-coords[0])/2 + coords[0], coords[2], (coords[3]-coords[2])/2 + coords[2]]
            coords2 = [(coords[1]-coords[0])/2 + coords[0], coords[1], coords[2], (coords[3]-coords[2])/2 + coords[2]]
            coords3 = [coords[0], (coords[1]-coords[0])/2 + coords[0], (coords[3]-coords[2])/2 + coords[2], coords[3]]
            coords4 = [(coords[1]-coords[0])/2 + coords[0], coords[1], (coords[3]-coords[2])/2 + coords[2], coords[3]]
            new_coords =[coords1,coords2,coords3,coords4]
            for coord in new_coords:
                post_data = {
                    "category": "cars",
                    "has-offers": False,
                    "place_lat_from": coord[0],
                    "place_lat_to": coord[1],
                    "place_lon_from": coord[2],
                    "place_lon_to": coord[3],
                    "section": "all"
                }
                yield Request(url="https://auto.ru/-/ajax/desktop/dealersListing/",cookies=cookies, 
                    headers=headers, callback=self.parse_dealer_links, method="POST", body=json.dumps(post_data), dont_filter=True, meta={'coords':coord})
        else:
            print(str(dealers['totalResultsCount']) + " results, storing links...")
            data = {}
            datas = []
            for dealer in dealers['dealers']:
                data['url'] = "https://auto.ru/diler/cars/all/" + dealer["dealerCode"]
                try:
                    data['logo'] = "https:" + dealer["dealerLogo"]
                except Exception:
                    data['logo'] = ""
                try:
                    data['Сеть'] = dealer["netName"]
                except Exception:
                    data['Сеть'] = ""
                try:
                    data['Адрес'] = dealer["address"]
                except Exception:
                    data['Адрес'] = ""
                try:
                    data['Метро'] = ""
                    for metro in dealer['metro']:
                        data['Метро'] += metro['name'] + ","
                    data['Метро'] = data['Метро'][:-1]
                except Exception:
                    data['Метро'] = ""
                try:
                    data['Авто в наличие'] = dealer["filteredOffersCount"]
                except Exception:
                    data['Авто в наличие'] = ""
                datas.append(data.copy())
            for data in datas:
               yield Request(data['url'], callback=self.parse_salon, meta={'data':data}, dont_filter=True)

    def parse(self,response):
        post_data = {
            "category": "cars",
            "has-offers": False,
            "place_lat_from": coords[0],
            "place_lat_to": coords[1],
            "place_lon_from": coords[2],
            "place_lon_to": coords[3],
            "section": "all"
        }
        # yield Request(url="https://auto.ru/-/ajax/desktop/dealersListing/",cookies=cookies, 
        #     headers=headers, callback=self.parse_dealer_links, method="POST", body=json.dumps(post_data), dont_filter=True, meta={'coords':coords})

        # #for test
        # url = "https://auto.ru/cars/used/sale/mazda/cx_5/1105799221-b29bcda9/"
        # url = "https://auto.ru/cars/used/sale/mazda/cx_5/1105652699-c437ec52/"
        # url = "https://auto.ru/cars/new/group/kia/sorento/22532657/23076832/1105066923-f42fdbfc/"
        # url = "https://auto.ru/cars/used/sale/smart/fortwo/1105214620-87c0a715"
        # yield SeleniumRequest(url=url, callback=self.parse_car, dont_filter=True)

        url = "https://auto.ru/diler-oficialniy/cars/used/avtomir_saratov_volkswagen/"
        yield Request(url, callback=self.parse_salon, dont_filter=True)

    def parse_salon(self, response):
        try:
            pages = response.css("a.ListingPagination__page::text").extract()[-1]
        except Exception:
            pages = 1
        link = response.url
        for page in range(1, int(pages)+1):
            yield Request(link + "?page=" + str(page), callback=self.parse_page, meta={'link':link}, dont_filter=True)

    def parse_page(self, response):
        link = response.meta['link']
        try:
            cars = response.css("a.ListingItemTitle__link::attr(href)").extract()
        except Exception:
            cars = []
        print(cars)
        for car in cars:
            yield SeleniumRequest(url=car, callback=self.parse_car,  meta={'link':link}, dont_filter=True)

    def parse_car(self, response):
        driver = response.request.meta['driver']

        data = {}
        try:
            data['dealer url'] = response.meta['link']
        except Exception:
            data['dealer url'] = ""

        try:
            data['car url'] = driver.current_url
        except Exception:
            data['car url'] = ""

        try:
            data['Тип авто'] = driver.find_elements_by_css_selector("div.CardBreadcrumbs__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
        except Exception:
            try:
                data['Тип авто'] = driver.find_elements_by_css_selector("li.BreadcrumbsGroup__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Тип авто'] = ""

        if data['Тип авто'] == "Б/у": 
            try:
                data['Номер'] = get_numbers(driver.find_elements_by_css_selector("div.CardHead__infoItem:nth-child(3)")[0].text)[0]
            except Exception:
                data['Номер'] = ""
            try:
                data['Марка'] = driver.find_elements_by_css_selector("div.CardBreadcrumbs__item:nth-child(4) > div:nth-child(1) > a:nth-child(1)")[0].text
            except Exception:
                data['Марка'] = ""
            try:
                data['Модель'] = driver.find_elements_by_css_selector("div.CardBreadcrumbs__item:nth-child(6) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Модель'] = ""

            try:
                data['Серия'] = driver.find_elements_by_css_selector("div.CardBreadcrumbs__item:nth-child(8) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Серия'] = ""
            try:
                data['Год выпуска'] = driver.find_elements_by_css_selector("li.CardInfoRow:nth-child(1) > span:nth-child(2) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Год выпуска'] = ""
            try:
                data['Цена'] = "".join(get_numbers(driver.find_elements_by_css_selector(".OfferPriceCaption__price")[0].text))
            except Exception:
                data['Цена'] = ""

            try:
                data['Цена со скидками'] = "".join(get_numbers(driver.find_elements_by_css_selector(".PriceUsedOffer__maxDiscount")[0].text))
            except Exception:
                data['Цена со скидками'] = ""
            action = ActionChains(driver)
            element = driver.find_elements_by_css_selector('.PriceUsedOffer__price')[0] 
            action.move_to_element(element)
            action.perform()
            try:
                driver.implicitly_wait(5)
                data['Цена в долларах'] = "".join(get_numbers(driver.find_elements_by_css_selector(".OfferPricePopupContent__priceItem")[0].text))
                driver.implicitly_wait(0)
            except Exception:
                data['Цена в долларах'] = ""
            try:
                data['Цена в евро'] = "".join(get_numbers(driver.find_elements_by_css_selector(".OfferPricePopupContent__priceItem")[1].text))
            except Exception:
                data['Цена в евро'] = ""
            try:
                data['Стоимость платежа кредита (руб/месяц)'] = "".join(get_numbers(driver.find_elements_by_css_selector(".OfferPricePopupContent__credit")[0].text))
            except Exception:
                data['Стоимость платежа кредита (руб/месяц)'] = ""
            keys = driver.find_elements_by_css_selector(".OfferDiscountOptions__itemName")
            values = driver.find_elements_by_css_selector(".OfferDiscountOptions__itemValue")
            keys = [elem.text for elem in keys]
            values = ["".join(get_numbers(elem.text)) for elem in values]
            data['В кредит'] = ""
            data['С каско'] = ""
            data['В трейд-ин'] = ""
            data['Максимальная'] = ""
            for id,key in enumerate(keys):
                if key == "В кредит":
                    data['В кредит'] = values[id]
                if key == "С каско":
                    data['С каско'] = values[id]
                if key == "В трейд-ин":
                    data['В трейд-ин'] = values[id]
                if key == "Максимальная":
                    data['Максимальная'] = values[id]
            try:
                data['Фото'] = ""
                photos = driver.find_elements_by_css_selector(".ImageGalleryDesktop__image-container > div > div > img")
                photos = [elem.get_attribute('src') for elem in photos]
                photos = set(photos)
                for photo in photos:
                    data['Фото'] += photo + ","
                data['Фото'] = data['Фото'][:-1]
            except Exception:
                data['Фото'] = ""

            try:
                data['Спецпредложения'] = ""
                elems = driver.find_elements_by_css_selector("a.CarouselSpecialNewItem__link")
                elems = [elem.get_attribute('href') for elem in elems]
                elems = set(elems)
                for elem in elems:
                    data['Спецпредложения'] += elem + ","
                data['Спецпредложения'] = data['Спецпредложения'][:-1]
            except Exception:
                data['Спецпредложения'] = ""

            try:
                data['Похожие автомобили'] = ""
                elems = driver.find_elements_by_css_selector("section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
                elems = [elem.get_attribute('href') for elem in elems]
                elems = set(elems)
                for elem in elems:
                    data['Похожие автомобили'] += elem + ","
                data['Похожие автомобили'] = data['Похожие автомобили'][:-1]
            except Exception:
                data['Похожие автомобили'] = ""

            try:
                driver.implicitly_wait(5)
                driver.find_elements_by_css_selector("span.SpoilerLink_type_default")[0].click()
                driver.implicitly_wait(0)
            except Exception:
                driver.implicitly_wait(0)


            keys = driver.find_elements_by_css_selector("div.CardBenefits__item-info-popup> div:nth-child(1) > div:nth-child(2) > div:nth-child(1)")
            values = driver.find_elements_by_css_selector("div.InfoPopup > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
            keys = [elem.text.strip() for elem in keys]
            values = [elem.text.strip() for elem in values]

            keys_strong = ["Дилер на связи", "Дилер готов торговаться", "Онлайн-показ", "Медленно теряет в цене"]
            for key in keys_strong:
                data[key] = "Нет"

            for id,key in enumerate(keys):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key] = "Да"
                            if key == "Медленно теряет в цене":
                                data[key] = get_numbers(values[-1])[0]
                        except Exception:
                            data[key1] = ""
                
            try:
                data['Комментарий продавца'] = driver.find_elements_by_css_selector(".CardDescriptionHTML")[0].get_attribute('innerHTML')
            except Exception:
                data['Комментарий продавца'] = ""
            
            keys_strong = ['Пробег', 'Кузов', 'Цвет', 'Налог', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Гарантия', 'Обмен']
            for key in keys_strong:
                data[key] = ""

            try:
                cats = driver.find_elements_by_css_selector("li.CardInfoRow > span:nth-child(1)")
                cats = [elem.text.strip() for elem in cats]
                cats = list(filter(None, cats))
                # print(cats)
            except Exception:
                cats = []

            values = driver.find_elements_by_css_selector("li.CardInfoRow > span:nth-child(2)")
            values = [elem.text.strip() for elem in values]
            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""

            try:
                url = driver.find_elements_by_css_selector(".CardCatalogLink")[0].get_attribute('href')
                yield SeleniumRequest(url=url, callback=self.parse_specifications,  meta={'data':data}, dont_filter=True)
            except Exception:
                pass
        

        if data['Тип авто'] == "Новые": 
            try:
                data['Номер'] = get_numbers(driver.find_elements_by_css_selector("div.CardHead__infoItem:nth-child(3)")[0].text)[0]
            except Exception:
                data['Номер'] = ""
            try:
                data['Марка'] = driver.find_elements_by_css_selector("li.BreadcrumbsGroup__item:nth-child(3) > a:nth-child(1)")[0].text
            except Exception:
                data['Марка'] = ""
            try:
                data['Модель'] = driver.find_elements_by_css_selector("li.BreadcrumbsGroup__item:nth-child(4) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Модель'] = ""

            try:
                data['Серия'] = driver.find_elements_by_css_selector("li.BreadcrumbsGroup__item:nth-child(5) > a:nth-child(1)")[0].text.strip()
            except Exception:
                data['Серия'] = ""
            try:
                data['Год выпуска'] = driver.find_elements_by_css_selector("div.CardHead__infoItem:nth-child(1)")[0].text.strip()
            except Exception:
                data['Год выпуска'] = ""
            try:
                data['Цена'] = "".join(get_numbers(driver.find_elements_by_css_selector(".PriceNewOffer__originalPrice")[0].text))
            except Exception:
                data['Цена'] = ""

            try:
                data['Цена со скидками'] = "".join(get_numbers(driver.find_elements_by_css_selector(".OfferPriceCaption")[0].text))
            except Exception:
                data['Цена со скидками'] = ""
            action = ActionChains(driver)
            element = driver.find_elements_by_css_selector('.PriceNewOffer__price')[0] 
            action.move_to_element(element)
            action.perform()

            try:
                driver.implicitly_wait(5)
                data['Цена в долларах'] = "".join(get_numbers(driver.find_elements_by_css_selector(".PriceNewOffer__priceItem")[0].text))
                driver.implicitly_wait(0)
            except Exception:
                data['Цена в долларах'] = ""
            try:
                data['Цена в евро'] = "".join(get_numbers(driver.find_elements_by_css_selector(".PriceNewOffer__priceItem")[1].text))
            except Exception:
                data['Цена в евро'] = ""
            data['Стоимость платежа кредита (руб/месяц)'] = ""
            
            keys = driver.find_elements_by_css_selector(".CardDiscountList__itemName")
            values = driver.find_elements_by_css_selector(".CardDiscountList__itemValue")
            keys = [elem.text for elem in keys]
            values = ["".join(get_numbers(elem.text)) for elem in values]
            data['В кредит'] = ""
            data['С каско'] = ""
            data['В трейд-ин'] = ""
            data['Максимальная'] = ""
            for id,key in enumerate(keys):
                if key == "В кредит":
                    data['В кредит'] = values[id]
                if key == "С каско":
                    data['С каско'] = values[id]
                if key == "В трейд-ин":
                    data['В трейд-ин'] = values[id]
                if key == "Максимальная":
                    data['Максимальная'] = values[id]

            try:
                data['Фото'] = ""
                photos = driver.find_elements_by_css_selector(".ImageGalleryDesktop__image-container > div > div > img")
                photos = [elem.get_attribute('src') for elem in photos]
                photos = set(photos)
                for photo in photos:
                    data['Фото'] += photo + ","
                data['Фото'] = data['Фото'][:-1]
            except Exception:
                data['Фото'] = ""

            try:
                data['Спецпредложения'] = ""
                elems = driver.find_elements_by_css_selector("a.CarouselSpecialNewItem__link")
                elems = [elem.get_attribute('href') for elem in elems]
                elems = set(elems)
                for elem in elems:
                    data['Спецпредложения'] += elem + ","
                data['Спецпредложения'] = data['Спецпредложения'][:-1]
            except Exception:
                data['Спецпредложения'] = ""

            try:
                data['Похожие автомобили'] = ""
                elems = driver.find_elements_by_css_selector("section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
                elems = [elem.get_attribute('href') for elem in elems]
                elems = set(elems)
                for elem in elems:
                    data['Похожие автомобили'] += elem + ","
                data['Похожие автомобили'] = data['Похожие автомобили'][:-1]
            except Exception:
                data['Похожие автомобили'] = ""

            keys_strong = ["Дилер на связи", "Дилер готов торговаться", "Онлайн-показ", "Медленно теряет в цене"]
            for key in keys_strong:
                data[key] = "Нет"
                
            try:
                data['Комментарий продавца'] = driver.find_elements_by_css_selector(".CardDescriptionHTML")[0].get_attribute('innerHTML')
            except Exception:
                data['Комментарий продавца'] = ""

            keys_strong = ['Пробег', 'Кузов', 'Цвет', 'Налог', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Гарантия', 'Обмен']
            for key in keys_strong:
                data[key] = ""

            try:
                cats = driver.find_elements_by_css_selector("div.CardInfoGroupedRow__cellTitle")
                cats = [elem.text.strip() for elem in cats]
                cats = list(filter(None, cats))
                # print(cats)
            except Exception:
                cats = []

            values = driver.find_elements_by_css_selector(".CardInfoGroupedRow__cellValue")
            values = [elem.text.strip() for elem in values]
            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""
            url = driver.find_elements_by_css_selector(".CardCatalogLink")[0].get_attribute('href')
            yield SeleniumRequest(url=url, callback=self.parse_specifications,  meta={'data':data}, dont_filter=True)

    def parse_specifications(self, response):
        driver = response.request.meta['driver']
        data = response.meta['data']

        elems = driver.find_elements_by_css_selector("tr.catalog-table__row")
        elems = [elem.get_attribute('class') for elem in elems]
        complectation_id = 0
        for id,elem in enumerate(elems):
            elem = elem.split(" ")
            for class_name in elem:
                if class_name == "catalog-table__row_active":
                    complectation_id = id
        for id,elem in enumerate(elems):
            elem = elem.split(" ")
            if len(elem) == 1:
                if id < complectation_id:
                    complectation_id1 = id
        if complectation_id != 0:
            data['Комплектация'] = driver.find_elements_by_css_selector("tr.catalog-table__row")[complectation_id1].text
        else:
            data['Комплектация'] = ""

        keys_strong = ['Объем', 'Мощность', 'Коробка', 'Тип двигателя', 'Топливо', 'Привод', 
                        'Страна марки', 'Класс автомобиля', 'Количество дверей', 'Количество мест', 
                        'Длина', 'Ширина', 'Высота', 'Колёсная база', 'Клиренс', 'Ширина передней колеи', 
                        'Ширина задней колеи', 'Размер колёс', 'Объем багажника мин/макс, л', 'Объём топливного бака, л', 
                        'Снаряженная масса, кг', 'Полная масса, кг', 'Количество передач', 
                        'Тип передней подвески', 'Тип задней подвески', 'Передние тормоза', 'Задние тормоза', 
                        'Максимальная скорость, км/ч', 'Разгон до 100 км/ч, с', 'Расход топлива, л город/трасса/смешанный', 
                        'Экологический класс', 'Выбросы CO2, г/км', 'Расположение двигателя', 
                        'Объем двигателя, см³', 'Тип наддува', 'Максимальная мощность, л.с./кВт при об/мин', 
                        'Максимальный крутящий момент, Н*м при об/мин', 'Расположение цилиндров', 'Количество цилиндров', 
                        'Число клапанов на цилиндр', 'Система питания двигателя', 'Степень сжатия', 
                        'Диаметр цилиндра и ход поршня, мм']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = driver.find_elements_by_css_selector(".list-values__label")
            cats = [elem.text.strip() for elem in cats]
            cats = list(filter(None, cats))
            # print(cats)
        except Exception:
            cats = []

        values = driver.find_elements_by_css_selector(".list-values__value")
        values = [elem.text.strip() for elem in values]
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""

        try:
            data['Размер передних колес'] = data['Размер колёс'].split(" ")[0]
            data['Размер задних колес']   = data['Размер колёс'].split(" ")[1]
        except Exception:
            data['Размер передних колес'] = data['Размер колёс']
            data['Размер задних колес']   = data['Размер колёс']
        del data['Размер колёс']

        try:
            data['Расход топлива городской цикл (л)'] = data['Расход топлива, л город/трасса/смешанный'].split("/")[0]
            data['Расход топлива загородный цикл (л)'] = data['Расход топлива, л город/трасса/смешанный'].split("/")[1]
            data['Расход топлива смешанный цикл (л)'] = data['Расход топлива, л город/трасса/смешанный'].split("/")[2]
        except Exception:
            data['Расход топлива городской цикл (л)'] = ""
            data['Расход топлива загородный цикл (л)'] = ""
            data['Расход топлива смешанный цикл (л)'] = ""
        del data['Расход топлива, л город/трасса/смешанный']

        try:
            data['Максимальная мощность'] = data['Максимальная мощность, л.с./кВт при об/мин'].split(' при ')[0]
            data['Обороты максимальной мощности'] = data['Максимальная мощность, л.с./кВт при об/мин'].split(' при ')[1]
        except Exception:
            data['Максимальная мощность'] = ""
            data['Обороты максимальной мощности'] = ""
        del data['Максимальная мощность, л.с./кВт при об/мин']

        try:
            data['Максимальный крутящий момент'] = data['Максимальный крутящий момент, Н*м при об/мин'].split(' при ')[0]
            data['Обороты максимального крутящего момента'] = data['Максимальный крутящий момент, Н*м при об/мин'].split(' при ')[1]
        except Exception:
            data['Максимальный крутящий момент'] = ""
            data['Обороты максимального крутящего момента'] = ""
        del data['Максимальный крутящий момент, Н*м при об/мин']

        try:
            data['Диаметр цилиндра'] = data['Диаметр цилиндра и ход поршня, мм'].split(' × ')[0]
            data['Ход поршня'] = data['Диаметр цилиндра и ход поршня, мм'].split(' × ')[1]
        except Exception:
            data['Диаметр цилиндра'] = ""
            data['Ход поршня'] = ""
        del data['Диаметр цилиндра и ход поршня, мм']

        keys_strong = ['Комфорт', 'Обзор', 'Безопасность', 'Защита от угона', 'Салон', 'Мультимедиа', 'Элементы экстерьера', 'Прочее']
        for key in keys_strong:
            data[key] = ""
        try:
            driver.implicitly_wait(4)
            driver.find_elements_by_css_selector('.tabs_view_classic > div:nth-child(3) > a:nth-child(1)')[0].click()
            cats = driver.find_elements_by_css_selector('div.catalog__package-group > h3.catalog__h3')
            cats = [elem.text.strip() for elem in cats]
            for id,key in enumerate(cats):
                for key1 in keys_strong:
                    if (key == key1):
                        try:
                            values = driver.find_elements_by_css_selector("div.catalog__package-group:nth-child(" +str(id + 2) + ") > ul > li")
                            driver.implicitly_wait(0)
                            values = [elem.text.strip() for elem in values]
                            for value in values:
                                data[key1] += value + ","
                            data[key1] = data[key1][:-1]
                        except Exception:
                            data[key1] = ""
            driver.implicitly_wait(0)
        except Exception:
            driver.implicitly_wait(0)
            cats = []

        yield data




        
















