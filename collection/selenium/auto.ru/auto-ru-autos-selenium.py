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
        data['?????? ????????'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
    except Exception:
        try:
            data['?????? ????????'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(2) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['?????? ????????'] = ""

    if data['?????? ????????'] == "??/??" or data['?????? ????????'] == "?? ????????????????": 
        try:
            data['??????????'] = get_numbers(driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(3)")[0].text)[0]
        except Exception:
            data['??????????'] = ""
        try:
            data['??????????'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(4) > div:nth-child(1) > a:nth-child(1)")[0].text
        except Exception:
            data['??????????'] = ""
        try:
            data['????????????'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(6) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['????????????'] = ""

        try:
            data['??????????'] = driver.find_elements(By.CSS_SELECTOR, "div.CardBreadcrumbs__item:nth-child(8) > div:nth-child(1) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['??????????'] = ""
        try:
            data['?????? ??????????????'] = driver.find_elements(By.CSS_SELECTOR, "li.CardInfoRow:nth-child(1) > span:nth-child(2) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['?????? ??????????????'] = ""
        try:
            # data['????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption__price")[0].text))
            data['????????'] = "".join(get_numbers(driver.find_element(By.CSS_SELECTOR, ".OfferPriceCaption__price").text))
        except Exception:
            data['????????'] = ""

        try:
            data['???????? ???? ????????????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceUsedOffer__maxDiscount")[0].text))
        except Exception:
            data['???????? ???? ????????????????'] = ""
        action = ActionChains(driver)
        try:
            element = driver.find_elements(By.CSS_SELECTOR, '.PriceUsedOffer__price')[0] 
            action.move_to_element(element)
            action.perform()
        except:
            print("sold")

        try:
            driver.implicitly_wait(5)
            data['???????? ?? ????????????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__priceItem")[0].text))
            driver.implicitly_wait(0)
        except Exception:
            data['???????? ?? ????????????????'] = ""
        try:
            data['???????? ?? ????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__priceItem")[1].text))
        except Exception:
            data['???????? ?? ????????'] = ""
        try:
            data['?????????????????? ?????????????? ?????????????? (??????/??????????)'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPricePopupContent__credit")[0].text))
        except Exception:
            data['?????????????????? ?????????????? ?????????????? (??????/??????????)'] = ""
        keys = driver.find_elements(By.CSS_SELECTOR, ".OfferDiscountOptions__itemName")
        values = driver.find_elements(By.CSS_SELECTOR, ".OfferDiscountOptions__itemValue")
        keys = [elem.text for elem in keys]
        values = ["".join(get_numbers(elem.text)) for elem in values]
        data['?? ????????????'] = ""
        data['?? ??????????'] = ""
        data['?? ??????????-????'] = ""
        data['????????????????????????'] = ""
        for id,key in enumerate(keys):
            if key == "?? ????????????":
                data['?? ????????????'] = values[id]
            if key == "?? ??????????":
                data['?? ??????????'] = values[id]
            if key == "?? ??????????-????":
                data['?? ??????????-????'] = values[id]
            if key == "????????????????????????":
                data['????????????????????????'] = values[id]
        data['????????'] = ""
        photo_new = ""
        try:
            photos = driver.find_elements(By.CSS_SELECTOR, ".ImageGalleryDesktop__image-container > div > div > img")
            photos = [elem.get_attribute('src') for elem in photos]
            for index,photo in enumerate(photos):
                local = uploadPhoto(photo, data['car url'], index)
                data['????????'] += photo + ","
                photo_new += local + ","
            data['????????'] = data['????????'][:-1]
            photo_new = photo_new[:-1]
            deletePhotos()
        except Exception:
            data['????????'] = ""
            photo_new = ""

        try:
            data['??????????????????????????????'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "a.CarouselSpecialNewItem__link")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['??????????????????????????????'] += elem + ","
            data['??????????????????????????????'] = data['??????????????????????????????'][:-1]
        except Exception:
            data['??????????????????????????????'] = ""

        try:
            data['?????????????? ????????????????????'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['?????????????? ????????????????????'] += elem + ","
            data['?????????????? ????????????????????'] = data['?????????????? ????????????????????'][:-1]
        except Exception:
            data['?????????????? ????????????????????'] = ""

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

        keys_strong = ["?????????? ???? ??????????", "?????????? ?????????? ??????????????????????", "????????????-??????????", "???????????????? ???????????? ?? ????????"]
        for key in keys_strong:
            data[key] = "??????"

        for id,key in enumerate(keys):
            if key == "?????????? ???????????? ???? ??????????":
                data["?????????? ???? ??????????"] = "????"
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key] = "????"
                        if key == "???????????????? ???????????? ?? ????????":
                            data[key] = get_numbers(values[-1])[0]
                    except Exception:
                        data[key1] = ""
            
        try:
            data['?????????????????????? ????????????????'] = driver.find_elements(By.CSS_SELECTOR, ".CardDescriptionHTML")[0].get_attribute('innerHTML')
        except Exception:
            data['?????????????????????? ????????????????'] = ""
        
        keys_strong = ['????????????', '??????????', '????????', '??????????', '????????', '??????????????????', '??????????????????', '??????', '??????????????', '????????????????', '??????????']
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

    if data['?????? ????????'] == "??????????": 
        try:
            data['??????????'] = get_numbers(driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(3)")[0].text)[0]
        except Exception:
            data['??????????'] = ""
        try:
            data['??????????'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(3) > a:nth-child(1)")[0].text
        except Exception:
            data['??????????'] = ""
        try:
            data['????????????'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(4) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['????????????'] = ""

        try:
            data['??????????'] = driver.find_elements(By.CSS_SELECTOR, "li.BreadcrumbsGroup__item:nth-child(5) > a:nth-child(1)")[0].text.strip()
        except Exception:
            data['??????????'] = ""
        try:
            data['?????? ??????????????'] = driver.find_elements(By.CSS_SELECTOR, "div.CardHead__infoItem:nth-child(1)")[0].text.strip()
        except Exception:
            data['?????? ??????????????'] = ""
        try:
            data['????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption__price")[0].text))
        except Exception:
            try:
                data['????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__originalPrice")[0].text))
            except Exception:
                data['????????'] = ""

        try:
            data['???????? ???? ????????????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".OfferPriceCaption")[0].text))
        except Exception:
            data['???????? ???? ????????????????'] = ""
        action = ActionChains(driver)

        try:
            element = driver.find_elements(By.CSS_SELECTOR, '.PriceNewOffer__price')[0] 
            action.move_to_element(element)
            action.perform()
        except:
            print("sold")

        try:
            driver.implicitly_wait(6)
            data['???????? ?? ????????????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__priceItem")[0].text))
            driver.implicitly_wait(0)
        except Exception:
            data['???????? ?? ????????????????'] = ""
        try:
            data['???????? ?? ????????'] = "".join(get_numbers(driver.find_elements(By.CSS_SELECTOR, ".PriceNewOffer__priceItem")[1].text))
        except Exception:
            data['???????? ?? ????????'] = ""
        data['?????????????????? ?????????????? ?????????????? (??????/??????????)'] = ""
        
        keys = driver.find_elements(By.CSS_SELECTOR, ".CardDiscountList__itemName")
        values = driver.find_elements(By.CSS_SELECTOR, ".CardDiscountList__itemValue")
        keys = [elem.text for elem in keys]
        values = ["".join(get_numbers(elem.text)) for elem in values]
        data['?? ????????????'] = ""
        data['?? ??????????'] = ""
        data['?? ??????????-????'] = ""
        data['????????????????????????'] = ""
        for id,key in enumerate(keys):
            if key == "?? ????????????":
                data['?? ????????????'] = values[id]
            if key == "?? ??????????":
                data['?? ??????????'] = values[id]
            if key == "?? ??????????-????":
                data['?? ??????????-????'] = values[id]
            if key == "????????????????????????":
                data['????????????????????????'] = values[id]

        data['????????'] = ""
        photo_new = ""
        try:
            photos = driver.find_elements(By.CSS_SELECTOR, ".ImageGalleryDesktop__image-container > div > div > img")
            photos = [elem.get_attribute('src') for elem in photos]
            for index,photo in enumerate(photos):
                local = uploadPhoto(photo, data['car url'], index)
                data['????????'] += photo + ","
                photo_new += local + ","
            data['????????'] = data['????????'][:-1]
            photo_new = photo_new[:-1]
            deletePhotos()
        except Exception:
            data['????????'] = ""
            photo_new = ""

        try:
            data['??????????????????????????????'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "a.CarouselSpecialNewItem__link")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['??????????????????????????????'] += elem + ","
            data['??????????????????????????????'] = data['??????????????????????????????'][:-1]
        except Exception:
            data['??????????????????????????????'] = ""

        try:
            data['?????????????? ????????????????????'] = ""
            elems = driver.find_elements(By.CSS_SELECTOR, "section.ListingSameGroupItem > div:nth-child(1) > a:nth-child(1)")
            elems = [elem.get_attribute('href') for elem in elems]
            elems = set(elems)
            for elem in elems:
                data['?????????????? ????????????????????'] += elem + ","
            data['?????????????? ????????????????????'] = data['?????????????? ????????????????????'][:-1]
        except Exception:
            data['?????????????? ????????????????????'] = ""

        keys = driver.find_elements(By.CSS_SELECTOR, "div.CardBenefits__item-info-popup> div:nth-child(1) > div:nth-child(2) > div:nth-child(1)")
        values = driver.find_elements(By.CSS_SELECTOR, "div.InfoPopup > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        keys = [elem.text.strip() for elem in keys]
        values = [elem.text.strip() for elem in values]

        keys_strong = ["?????????? ???? ??????????", "?????????? ?????????? ??????????????????????", "????????????-??????????", "???????????????? ???????????? ?? ????????"]
        for key in keys_strong:
            data[key] = "??????"

        for id,key in enumerate(keys):
            if key == "?????????? ???????????? ???? ??????????":
                data["?????????? ???? ??????????"] = "????"
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key] = "????"
                        if key == "???????????????? ???????????? ?? ????????":
                            data[key] = get_numbers(values[-1])[0]
                    except Exception:
                        data[key1] = ""
            
        try:
            data['?????????????????????? ????????????????'] = driver.find_elements(By.CSS_SELECTOR, ".CardDescriptionHTML")[0].get_attribute('innerHTML')
        except Exception:
            data['?????????????????????? ????????????????'] = ""

        keys_strong = ['????????????', '??????????', '????????', '??????????', '????????', '??????????????????', '??????????????????', '??????', '??????????????', '????????????????', '??????????']
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
        data['????????????????????????'] = driver.find_elements(By.CSS_SELECTOR, "tr.catalog-table__row")[complectation_id1].text
    else:
        data['????????????????????????'] = ""

    keys_strong = ['??????????', '????????????????', '??????????????', '?????? ??????????????????', '??????????????', '????????????', 
                    '???????????? ??????????', '?????????? ????????????????????', '???????????????????? ????????????', '???????????????????? ????????', 
                    '??????????', '????????????', '????????????', '???????????????? ????????', '??????????????', '???????????? ???????????????? ??????????', 
                    '???????????? ???????????? ??????????', '???????????? ??????????', '?????????? ?????????????????? ??????/????????, ??', '?????????? ???????????????????? ????????, ??', 
                    '?????????????????????? ??????????, ????', '???????????? ??????????, ????', '???????????????????? ??????????????', 
                    '?????? ???????????????? ????????????????', '?????? ???????????? ????????????????', '???????????????? ??????????????', '???????????? ??????????????', 
                    '???????????????????????? ????????????????, ????/??', '???????????? ???? 100 ????/??, ??', '???????????? ??????????????, ?? ??????????/????????????/??????????????????', 
                    '?????????????????????????? ??????????', '?????????????? CO2, ??/????', '???????????????????????? ??????????????????', 
                    '?????????? ??????????????????, ??????', '?????? ??????????????', '???????????????????????? ????????????????, ??.??./?????? ?????? ????/??????', 
                    '???????????????????????? ???????????????? ????????????, ??*?? ?????? ????/??????', '???????????????????????? ??????????????????', '???????????????????? ??????????????????', 
                    '?????????? ???????????????? ???? ??????????????', '?????????????? ?????????????? ??????????????????', '?????????????? ????????????', 
                    '?????????????? ???????????????? ?? ?????? ????????????, ????']
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
        data['???????????? ???????????????? ??????????'] = data['???????????? ??????????'].split(" ")[0]
        data['???????????? ???????????? ??????????']   = data['???????????? ??????????'].split(" ")[1]
    except Exception:
        data['???????????? ???????????????? ??????????'] = data['???????????? ??????????']
        data['???????????? ???????????? ??????????']   = data['???????????? ??????????']
    del data['???????????? ??????????']

    try:
        data['???????????? ?????????????? ?????????????????? ???????? (??)'] = data['???????????? ??????????????, ?? ??????????/????????????/??????????????????'].split("/")[0]
        data['???????????? ?????????????? ???????????????????? ???????? (??)'] = data['???????????? ??????????????, ?? ??????????/????????????/??????????????????'].split("/")[1]
        data['???????????? ?????????????? ?????????????????? ???????? (??)'] = data['???????????? ??????????????, ?? ??????????/????????????/??????????????????'].split("/")[2]
    except Exception:
        data['???????????? ?????????????? ?????????????????? ???????? (??)'] = ""
        data['???????????? ?????????????? ???????????????????? ???????? (??)'] = ""
        data['???????????? ?????????????? ?????????????????? ???????? (??)'] = ""
    del data['???????????? ??????????????, ?? ??????????/????????????/??????????????????']

    try:
        data['???????????????????????? ????????????????'] = data['???????????????????????? ????????????????, ??.??./?????? ?????? ????/??????'].split(' ?????? ')[0]
        data['?????????????? ???????????????????????? ????????????????'] = data['???????????????????????? ????????????????, ??.??./?????? ?????? ????/??????'].split(' ?????? ')[1]
    except Exception:
        data['???????????????????????? ????????????????'] = ""
        data['?????????????? ???????????????????????? ????????????????'] = ""
    del data['???????????????????????? ????????????????, ??.??./?????? ?????? ????/??????']

    try:
        data['???????????????????????? ???????????????? ????????????'] = data['???????????????????????? ???????????????? ????????????, ??*?? ?????? ????/??????'].split(' ?????? ')[0]
        data['?????????????? ?????????????????????????? ?????????????????? ??????????????'] = data['???????????????????????? ???????????????? ????????????, ??*?? ?????? ????/??????'].split(' ?????? ')[1]
    except Exception:
        data['???????????????????????? ???????????????? ????????????'] = ""
        data['?????????????? ?????????????????????????? ?????????????????? ??????????????'] = ""
    del data['???????????????????????? ???????????????? ????????????, ??*?? ?????? ????/??????']

    try:
        data['?????????????? ????????????????'] = data['?????????????? ???????????????? ?? ?????? ????????????, ????'].split(' ?? ')[0]
        data['?????? ????????????'] = data['?????????????? ???????????????? ?? ?????? ????????????, ????'].split(' ?? ')[1]
    except Exception:
        data['?????????????? ????????????????'] = ""
        data['?????? ????????????'] = ""
    del data['?????????????? ???????????????? ?? ?????? ????????????, ????']

    keys_strong = ['??????????????', '??????????', '????????????????????????', '???????????? ???? ??????????', '??????????', '??????????????????????', '???????????????? ????????????????????', '????????????']
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
    data['??????????'] = city
    data['???????? ?????????????????? ??????'] = photo_new
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

    keys = ["dealer url","car url","?????? ????????","??????????","??????????","????????????","??????????","?????? ??????????????","????????",
            "???????? ???? ????????????????","???????? ?? ????????????????","???????? ?? ????????","?????????????????? ?????????????? ?????????????? (??????/??????????)",
            "?? ????????????","?? ??????????","?? ??????????-????","????????????????????????","????????","??????????????????????????????","?????????????? ????????????????????",
            "?????????? ???? ??????????","?????????? ?????????? ??????????????????????","????????????-??????????","???????????????? ???????????? ?? ????????",
            "?????????????????????? ????????????????","????????????","??????????","????????","??????????","????????","??????????????????","??????????????????","??????",
            "??????????????","????????????????","??????????","????????????????????????","??????????","????????????????","??????????????","?????? ??????????????????","??????????????",
            "????????????","???????????? ??????????","?????????? ????????????????????","???????????????????? ????????????","???????????????????? ????????","??????????","????????????",
            "????????????","???????????????? ????????","??????????????","???????????? ???????????????? ??????????","???????????? ???????????? ??????????","?????????? ?????????????????? ??????/????????, ??",
            "?????????? ???????????????????? ????????, ??","?????????????????????? ??????????, ????","???????????? ??????????, ????","???????????????????? ??????????????",
            "?????? ???????????????? ????????????????","?????? ???????????? ????????????????","???????????????? ??????????????","???????????? ??????????????","???????????????????????? ????????????????, ????/??",
            "???????????? ???? 100 ????/??, ??","?????????????????????????? ??????????","?????????????? CO2, ??/????","???????????????????????? ??????????????????",
            "?????????? ??????????????????, ??????","?????? ??????????????","???????????????????????? ??????????????????","???????????????????? ??????????????????",
            "?????????? ???????????????? ???? ??????????????","?????????????? ?????????????? ??????????????????","?????????????? ????????????","???????????? ???????????????? ??????????",
            "???????????? ???????????? ??????????","???????????? ?????????????? ?????????????????? ???????? (??)","???????????? ?????????????? ???????????????????? ???????? (??)",
            "???????????? ?????????????? ?????????????????? ???????? (??)","???????????????????????? ????????????????","?????????????? ???????????????????????? ????????????????",
            "???????????????????????? ???????????????? ????????????","?????????????? ?????????????????????????? ?????????????????? ??????????????","?????????????? ????????????????",
            "?????? ????????????","??????????????","??????????","????????????????????????","???????????? ???? ??????????","??????????","??????????????????????",
            "???????????????? ????????????????????","????????????", "??????????", "???????? ?????????????????? ??????"]


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






        
















