import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json

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
    name = 'avto-ru'
    allowed_domains = ['avto.ru']
    start_urls =["https://auto.ru/dilery/cars/all/"]

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
                    data['????????'] = dealer["netName"]
                except Exception:
                    data['????????'] = ""
                try:
                    data['??????????'] = dealer["address"]
                except Exception:
                    data['??????????'] = ""
                try:
                    data['??????????'] = ""
                    for metro in dealer['metro']:
                        data['??????????'] += metro['name'] + ","
                    data['??????????'] = data['??????????'][:-1]
                except Exception:
                    data['??????????'] = ""
                try:
                    data['???????? ?? ??????????????'] = dealer["filteredOffersCount"]
                except Exception:
                    data['???????? ?? ??????????????'] = ""
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
        yield Request(url="https://auto.ru/-/ajax/desktop/dealersListing/",cookies=cookies, 
            headers=headers, callback=self.parse_dealer_links, method="POST", body=json.dumps(post_data), dont_filter=True, meta={'coords':coords})

    def parse_salon(self, response):
        data = response.meta['data']

        data['???????????????? ????????????????????'] = response.css(".SalonHeader__title::text").extract_first()

        if (response.css("li.SalonHeader__descriptionItem:nth-child(1) > span:nth-child(2)::text").extract_first().find("????????????") != -1):
            data['?????? ????????'] = "?? ????????????????"
        else:
            data['?????? ????????'] = "??????????"

        try:
            data['???????????? ????????????'] = response.css("li.SalonHeader__descriptionItem:nth-child(3) > span:nth-child(2)::text").extract_first().strip()
        except Exception:
            data['???????????? ????????????'] = ""

        data['?????????????????????? ??????????'] = "??????"
        data['?????????????????????? ?????????? ?????????? ??????????'] = ""
        values = response.css("li.SalonHeader__infoItem > span::text").extract()
        for value in values:
            value = value.strip()
            if value.find("?????????????????????? ??????????") != -1:
                data['?????????????????????? ??????????'] = "????"
            if value.find("?????????????????????? ?????????? ") != -1:
                data['?????????????????????? ?????????? ?????????? ??????????'] = value[len("?????????????????????? ?????????? "):]

        try:
            data['????????'] = ""
            photos = response.css("li.CarouselUniversal__item > div:nth-child(1) > img:nth-child(1)::attr(src)").extract()
            photos = set(photos)
            for photo in photos:
                data['????????'] += "https:" + photo.replace("wizardv3mr",  "cattouchret") + ","

            data['????????'] = data['????????'][:-1]
        except Exception:
            data['????????'] = ""

        try:
            marks_json = response.text
            marks_json = marks_json[marks_json.find('"breadcrumbsPublicApi":{"data":[{"entities":[{"count":') + 32 : marks_json.find('}],"levelFilterParams":{"mark":')]
            marks_json += '}]}'
            try:
                marks_json = json.loads(marks_json)
            except Exception:
                marks_json = response.text
                marks_json = marks_json[marks_json.find('"breadcrumbsPublicApi":{"data":[{"entities":') + 32 : marks_json.find('],"status":"SUCCESS"},"bunker"')]
                marks_json = json.loads(marks_json)
            data['?????????? ????????'] = ""
            for mark in marks_json['entities']:
                data['?????????? ????????'] += mark['name'] + ","
            data['?????????? ????????'] = data['?????????? ????????'][:-1]
        except:
            data['?????????? ????????'] = ""

        code = data['url'].split("/")[-1]

        post_data = {
            'code': code, 
            'category': 'cars', 
            'section': 'all'
        }

        yield Request(url="https://auto.ru/-/ajax/desktop/getSalonPhones/",cookies=cookies, 
            headers=headers, callback=self.parse_phone, method="POST", body=json.dumps(post_data),  meta={'data1':data}, dont_filter=True)
        
    def parse_phone(self, response):
        data = response.meta['data1']
        phones = json.loads(response.text)
        try:
            data['????????????????'] = ""
            for phone in phones:
                temp = "".join(get_numbers(phone['phone']))
                temp = '8' + temp[1:]
                data['????????????????'] += temp + ","
            data['????????????????'] = data['????????????????'][:-1]
        except Exception:
            data['????????????????'] = ""
        print(phones)   
        yield data  















