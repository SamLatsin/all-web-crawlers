import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import re
import math
import json
import csv
import urllib.request
import requests
import boto3
import pickle

file_name = "avto_ru_cars.csv"

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())

def get_numbers(text):
    return re.findall(r'\d+', text)

def uploadToCloud(name):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id='YCAJEVUI8MhS424n9P0MCIjjF',
        aws_secret_access_key='YCOEPssN70yPUO_jcK1m31QVNgBO0O2QMfyO0UkW',
    )
    s3.upload_file(name, 'autosalons', "autos/" + name)
    return

def uploadPhoto(photo, orig, index):
    prefix = orig.split("/")[-2]
    name = prefix + "-" + str(index) + ".webp"
    urllib.request.urlretrieve(photo, name)
    uploadToCloud(name)
    return name

def deletePhotos():
    for file in os.listdir():
        if file.endswith('.webp'):
            os.remove(file)

def apiImport(data):
    token = "xLmxLZ7Sk3vqPBrsWUyb5hrZDqmLzRkz"
    new_data = []
    for key in data:
        new_data.append(data[key])

    data = {
        'token': token,
        'data': json.dumps(new_data)
    }
    response = requests.post('http://panel.autosalons.ru/parsing/import_car_raw', data=data)
    return

def parse_car(driver, data):
    # data = {}
    # try:
    #     data['dealer url'] = response.meta['link']
    # except Exception:
    #     data['dealer url'] = ""

    # try:
    #     data['car url'] = driver.current_url
    # except Exception:
    #     data['car url'] = ""
    print("getting: " + data['car url'])
    driver.get(data['car url'])
    pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

    try:
        city = driver.find_elements(By.CSS_SELECTOR, ".MetroListPlace__regionName")[0].text.strip()
    except Exception:
        city = "" 

    try:
        data['Тип авто'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
    except Exception:
        try:
            data['Тип авто'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Тип авто'] = ""

    if data['Тип авто'] == "Б/у" or data['Тип авто'] == "С пробегом": 
        try:
            data['Номер'] = get_numbers(driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(3)")[0].text)[0]
        except Exception:
            data['Номер'] = ""
        try:
            data['Марка'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(4) > div:nth-child(1) > a:nth-child(1)")[0].text
        except Exception:
            data['Марка'] = ""
        try:
            data['Модель'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(6) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Модель'] = ""

        try:
            data['Серия'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(8) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Серия'] = ""
        try:
            data['Год выпуска'] = driver.find_elements(By.CSS_SELECTOR, "li.CardInfoRow:nth-child(1) > span:nth-child(2) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Год выпуска'] = ""
        try:
            # data['Цена'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption__price")[0].text))
            data['Цена'] = "".join(get_numbers(driver.find_element(By.CSS_SELECTOR, ".OfferPriceCaption__price").text))
        except Exception:
            data['Цена'] = ""

        try:
            data['Цена со скидками'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceUsedOffer__maxDiscount")[0].text))
        except Exception:
            data['Цена со скидками'] = ""
        action = ActionChains(driver)
        try:
            element = driver.find_elements(By.CSS_SELECTOR, '.PriceUsedOffer__price')[0] 
            action.move_to_element(element)
            action.perform()
        except:
            print("sold")

        try:
            driver.implicitly_wait(5)
            data['Цена в долларах'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__priceItem")[0].text))
            driver.implicitly_wait(0)
        except Exception:
            data['Цена в долларах'] = ""
        try:
            data['Цена в евро'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__priceItem")[1].text))
        except Exception:
            data['Цена в евро'] = ""
        try:
            data['Стоимость платежа кредита (руб/месяц)'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__credit")[0].text))
        except Exception:
            data['Стоимость платежа кредита (руб/месяц)'] = ""
        keys = driver.find_elements(By.CSS_SELECTOR, ".OfferDiscountOptions__itemName")
        values = driver.find_elements(By.CSS_SELECTOR, ".OfferDiscountOptions__itemValue")
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
        data['Фото'] = ""
        photo_new = ""
        try:
            photos = driver.find_elements(By.CSS_SELECTOR, ".ImageGalleryDesktop__image-container > div > div > img")
            photos = [elem.get_attribute('src') for elem in photos]
            for index,photo in enumerate(photos):
                local = uploadPhoto(photo, data['car url'], index)
                data['Фото'] += photo + ","
                photo_new += local + ","
            data['Фото'] = data['Фото'][:-1]
            photo_new = photo_new[:-1]
            deletePhotos()
        except Exception:
            data['Фото'] = ""
            photo_new = ""

        try:
            data['Спецпредложения'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "a.CarouselSpecialNewItem__link")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['Спецпредложения'] += elem + ","
            data['Спецпредложения'] = data['Спецпредложения'][:-1]
        except Exception:
            data['Спецпредложения'] = ""

        try:
            data['Похожие автомобили'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['Похожие автомобили'] += elem + ","
            data['Похожие автомобили'] = data['Похожие автомобили'][:-1]
        except Exception:
            data['Похожие автомобили'] = ""

        try:
            driver.implicitly_wait(5)
            driver.find_elements(By.CSS_SELECTOR, "span.SpoilerLink_type_default")[0].click()
            driver.implicitly_wait(0)
        except Exception:
            driver.implicitly_wait(0)


        keys = driver.find_elements(By.CSS_SELECTOR, "div.CardBenefits__item-info-popup> div:nth-child(1) > div:nth-child(2) > div:nth-child(1)")
        values = driver.find_elements(By.CSS_SELECTOR, "div.InfoPopup > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        keys = [elem.text.strip() for elem in keys]
        values = [elem.text.strip() for elem in values]

        keys_strong = ["Дилер на связи", "Дилер готов торговаться", "Онлайн-показ", "Медленно теряет в цене"]
        for key in keys_strong:
            data[key] = "Нет"

        for id,key in enumerate(keys):
            if key == "Дилер всегда на связи":
                data["Дилер на связи"] = "Да"
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key] = "Да"
                        if key == "Медленно теряет в цене":
                            data[key] = get_numbers(values[-1])[0]
                    except Exception:
                        data[key1] = ""
            
        try:
            data['Комментарий продавца'] = driver.find_elements(By.CSS_SELECTOR, ".CardDescriptionHTML")[0].get_attribute('innerHTML')
        except Exception:
            data['Комментарий продавца'] = ""
        
        keys_strong = ['Пробег', 'Кузов', 'Цвет', 'Налог', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Гарантия', 'Обмен']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = driver.find_elements(By.CSS_SELECTOR, "li.CardInfoRow > span:nth-child(1)")
            cats = [elem.text.strip() for elem in cats]
            cats = list(filter(None, cats))
            # print(cats)
        except Exception:
            cats = []

        values = driver.find_elements(By.CSS_SELECTOR, "li.CardInfoRow > span:nth-child(2)")
        values = [elem.text.strip() for elem in values]
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""
        url = driver.find_elements(By.CSS_SELECTOR, ".CardCatalogLink")[0].get_attribute('href')
        driver.get(url)

    if data['Тип авто'] == "Новые": 
        try:
            data['Номер'] = get_numbers(driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(3)")[0].text)[0]
        except Exception:
            data['Номер'] = ""
        try:
            data['Марка'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(3) > a:nth-child(1)")[0].text
        except Exception:
            data['Марка'] = ""
        try:
            data['Модель'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(4) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Модель'] = ""

        try:
            data['Серия'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(5) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['Серия'] = ""
        try:
            data['Год выпуска'] = driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(1)")[0].text.strip()
        except Exception:
            data['Год выпуска'] = ""
        try:
            data['Цена'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption__price")[0].text))
        except Exception:
            try:
                data['Цена'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__originalPrice")[0].text))
            except Exception:
                data['Цена'] = ""

        try:
            data['Цена со скидками'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption")[0].text))
        except Exception:
            data['Цена со скидками'] = ""
        action = ActionChains(driver)

        try:
            element = driver.find_elements(By.CSS_SELECTOR, '.PriceNewOffer__price')[0] 
            action.move_to_element(element)
            action.perform()
        except:
            print("sold")

        try:
            driver.implicitly_wait(6)
            data['Цена в долларах'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__priceItem")[0].text))
            driver.implicitly_wait(0)
        except Exception:
            data['Цена в долларах'] = ""
        try:
            data['Цена в евро'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__priceItem")[1].text))
        except Exception:
            data['Цена в евро'] = ""
        data['Стоимость платежа кредита (руб/месяц)'] = ""
        
        keys = driver.find_elements(By.CSS_SELECTOR, ".CardDiscountList__itemName")
        values = driver.find_elements(By.CSS_SELECTOR, ".CardDiscountList__itemValue")
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

        data['Фото'] = ""
        photo_new = ""
        try:
            photos = driver.find_elements(By.CSS_SELECTOR, ".ImageGalleryDesktop__image-container > div > div > img")
            photos = [elem.get_attribute('src') for elem in photos]
            for index,photo in enumerate(photos):
                local = uploadPhoto(photo, data['car url'], index)
                data['Фото'] += photo + ","
                photo_new += local + ","
            data['Фото'] = data['Фото'][:-1]
            photo_new = photo_new[:-1]
            deletePhotos()
        except Exception:
            data['Фото'] = ""
            photo_new = ""

        try:
            data['Спецпредложения'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "a.CarouselSpecialNewItem__link")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['Спецпредложения'] += elem + ","
            data['Спецпредложения'] = data['Спецпредложения'][:-1]
        except Exception:
            data['Спецпредложения'] = ""

        try:
            data['Похожие автомобили'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['Похожие автомобили'] += elem + ","
            data['Похожие автомобили'] = data['Похожие автомобили'][:-1]
        except Exception:
            data['Похожие автомобили'] = ""

        keys = driver.find_elements(By.CSS_SELECTOR, "div.CardBenefits__item-info-popup> div:nth-child(1) > div:nth-child(2) > div:nth-child(1)")
        values = driver.find_elements(By.CSS_SELECTOR, "div.InfoPopup > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        keys = [elem.text.strip() for elem in keys]
        values = [elem.text.strip() for elem in values]

        keys_strong = ["Дилер на связи", "Дилер готов торговаться", "Онлайн-показ", "Медленно теряет в цене"]
        for key in keys_strong:
            data[key] = "Нет"

        for id,key in enumerate(keys):
            if key == "Дилер всегда на связи":
                data["Дилер на связи"] = "Да"
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key] = "Да"
                        if key == "Медленно теряет в цене":
                            data[key] = get_numbers(values[-1])[0]
                    except Exception:
                        data[key1] = ""
            
        try:
            data['Комментарий продавца'] = driver.find_elements(By.CSS_SELECTOR, ".CardDescriptionHTML")[0].get_attribute('innerHTML')
        except Exception:
            data['Комментарий продавца'] = ""

        keys_strong = ['Пробег', 'Кузов', 'Цвет', 'Налог', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Гарантия', 'Обмен']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = driver.find_elements(By.CSS_SELECTOR, "div.CardInfoGroupedRow__cellTitle")
            cats = [elem.text.strip() for elem in cats]
            cats = list(filter(None, cats))
            # print(cats)
        except Exception:
            cats = []

        values = driver.find_elements(By.CSS_SELECTOR, ".CardInfoGroupedRow__cellValue")
        values = [elem.text.strip() for elem in values]
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""
        url = driver.find_elements(By.CSS_SELECTOR, ".CardCatalogLink")[0].get_attribute('href')
        driver.get(url)

    elems = driver.find_elements(By.CSS_SELECTOR, "tr.catalog-table__row")
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
        data['Комплектация'] = driver.find_elements(By.CSS_SELECTOR, "tr.catalog-table__row")[complectation_id1].text
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
        cats = driver.find_elements(By.CSS_SELECTOR, ".list-values__label")
        cats = [elem.text.strip() for elem in cats]
        cats = list(filter(None, cats))
        # print(cats)
    except Exception:
        cats = []

    values = driver.find_elements(By.CSS_SELECTOR, ".list-values__value")
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
        driver.find_elements(By.CSS_SELECTOR, '.tabs_view_classic > div:nth-child(3) > a:nth-child(1)')[0].click()
        cats = driver.find_elements(By.CSS_SELECTOR, 'div.catalog__package-group > h3.catalog__h3')
        cats = [elem.text.strip() for elem in cats]
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        values = driver.find_elements(By.CSS_SELECTOR, "div.catalog__package-group:nth-child(" +str(id + 2) + ") > ul > li")
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
    data['Город'] = city
    data['Фото локальное имя'] = photo_new
    print("success")
    print(data)
    apiImport(data)
    with open(file_name, 'a', encoding = 'utf-8') as f:
        w = csv.DictWriter(f, data.keys())
        w.writerow(data)

def parse_dealer(driver, data):
    print("getting: " + data['dealer url'])
    driver.get(data['dealer url'])
    try:        
        pages = driver.find_elements(By.CSS_SELECTOR, "a.ListingPagination__page")[-1].text
    except:
        pages = 1
    for page in range(1, int(pages)+1):
        driver.get(data['dealer url'] + "?page=" + str(page))
        elems = driver.find_elements(By.CSS_SELECTOR, "a.ListingItemTitle__link")
        elems = [elem.get_attribute('href') for elem in elems]
        elems = set(elems)
        for elem in elems:
            data['car url'] = elem
            parse_car(driver, data)

def main(driver, start_line):
    # data = {}
    # data[' dealer url'] = "https://auto.ru/diler/cars/new/rolf_volgogradskiy_td_moskva/"
    # data['car url'] = "https://auto.ru/cars/new/group/audi/q8/21519841/21520421/1115367572-3ffca292/"
    # parse_car(driver, data)
    # start_line = 0
    with open(r"input.csv", encoding = 'utf-8') as f:
        links = [url.strip().split(",") for url in f.readlines()]   
        links = links[1:] 
        # links = links[7:8] 
        data = {}
        line = 0
        for link in links:
            line += 1

            with open(r"start_line.txt", 'w') as f:
                f.write(str(line))

            if line > start_line:
                print(line)
                data['dealer url'] = link[0]
                parse_dealer(driver, data)
                # data['car url'] = link[1]
                # parse_car(driver, data)

        with open(r"start_line.txt", 'w') as f:
            f.write("0")

if __name__ == "__main__":
    options = Options()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.http.pipelining", True)
    profile.set_preference("network.http.proxy.pipelining", True)
    profile.set_preference("network.http.pipelining.maxrequests", 8)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
    profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
    profile.set_preference("loop.enabled", False)
    profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
    profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
    profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
    profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
    profile.set_preference("browser.display.use_system_colors", True) # Use system colors.
    profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0) # blank
    profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
    profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
    profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
    profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
    profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
    profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("permissions.default.image", 2) # Image load disabled again

    profile.set_preference("permissions.default.stylesheet", 2);

    options.headless = False

    keys = ["dealer url","car url","Тип авто","Номер","Марка","Модель","Серия","Год выпуска","Цена",
            "Цена со скидками","Цена в долларах","Цена в евро","Стоимость платежа кредита (руб/месяц)",
            "В кредит","С каско","В трейд-ин","Максимальная","Фото","Спецпредложения","Похожие автомобили",
            "Дилер на связи","Дилер готов торговаться","Онлайн-показ","Медленно теряет в цене",
            "Комментарий продавца","Пробег","Кузов","Цвет","Налог","Руль","Состояние","Владельцы","ПТС",
            "Таможня","Гарантия","Обмен","Комплектация","Объем","Мощность","Коробка","Тип двигателя","Топливо",
            "Привод","Страна марки","Класс автомобиля","Количество дверей","Количество мест","Длина","Ширина",
            "Высота","Колёсная база","Клиренс","Ширина передней колеи","Ширина задней колеи","Объем багажника мин/макс, л",
            "Объём топливного бака, л","Снаряженная масса, кг","Полная масса, кг","Количество передач",
            "Тип передней подвески","Тип задней подвески","Передние тормоза","Задние тормоза","Максимальная скорость, км/ч",
            "Разгон до 100 км/ч, с","Экологический класс","Выбросы CO2, г/км","Расположение двигателя",
            "Объем двигателя, см³","Тип наддува","Расположение цилиндров","Количество цилиндров",
            "Число клапанов на цилиндр","Система питания двигателя","Степень сжатия","Размер передних колес",
            "Размер задних колес","Расход топлива городской цикл (л)","Расход топлива загородный цикл (л)",
            "Расход топлива смешанный цикл (л)","Максимальная мощность","Обороты максимальной мощности",
            "Максимальный крутящий момент","Обороты максимального крутящего момента","Диаметр цилиндра",
            "Ход поршня","Комфорт","Обзор","Безопасность","Защита от угона","Салон","Мультимедиа",
            "Элементы экстерьера","Прочее", "Город", "Фото локальное имя"]


    with open(r"start_line.txt", encoding = 'utf-8') as f:
        start_line = int(f.readlines()[0])

    if (start_line == 0):
        with open(file_name, 'w') as f:
            w = csv.DictWriter(f, keys)
            w.writeheader()

    # make headless work
    driver = webdriver.Firefox(options = options, firefox_profile = profile)
    try:
        main(driver, start_line)
        driver.close()
    except Exception:
        try:
            driver.close()
        except Exception:
            pass
        print("error")
        os.system("python3 auto-ru-autos-selenium.py")






        
















