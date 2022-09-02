import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
from scrapy.http import HtmlResponse
import base64

token = '636224dafc34b7e0c38f88d0e90b7d6de0789c68d439dfb3'
uid = '3681872781632383078'
# spravka = 'dD0xNjQ5NzUxNDEwO2k9MTc2LjU5LjE3Mi44MjtEPUZEQUU0RDQ1MDVGNENGQUI5NTIwMjMzMDQzQjhFMzA0RDI4REQ3Mjk0QURGMDRENzg0MTc2QzQwMjdFMUVCMjQwRUM0NUI2MTt1PTE2NDk3NTE0MTA2NDM4ODAxNzU7aD1kMDQzYzU0NzA2ZTZhNjc5M2UzZDkwYjRiZGEyMzhiNQ=='
coords = [38, 76, 18, 165] # Russia coords
ip = '176.59.172.82'

cookies = {
    '_csrf_token': token,
    'yandexuid': uid,
    # 'spravka': spravka,
    'yandex_login': '',
}

headers = {
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Content-Type': 'application/json; charset=UTF-8',
    'x-csrf-token': token,
}

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

def generateIp(prev):
    ip = prev.split(".")
    ip[0] = int(ip[0])
    ip[1] = int(ip[1])
    ip[2] = int(ip[2])
    ip[3] = int(ip[3])
    ip[3] += 1
    if ip[3] == 256:
        ip[3] = 0
        ip[2] += 1
    if ip[2] == 256:
        ip[2] = 0
        ip[1] += 1
    if ip[1] == 256:
        ip[1] = 0
        ip[0] += 1
    if ip[0] == 256:
        ip = [0,0,0,0]
    ip[0] = str(ip[0])
    ip[1] = str(ip[1])
    ip[2] = str(ip[2])
    ip[3] = str(ip[3])
    ip = '.'.join(ip)
    return ip

def generateSpavka(ip):
    start = "t=1618219933;i="
    end = ";D=848228DEBE0820E0245D97448D68E6E44A4EC73741D3AAE5F09550B0329355F8A56E7CD0;u=1618219933614940517;h=01b771447d0c4b1fd02f38eebf104295"
    final = start + ip + end
    return base64.b64encode(final.encode("UTF-8")).decode('ascii')

class AvtodomSpider(scrapy.Spider):
    name = 'avto-ru-auto-links'
    allowed_domains = ['avto.ru']

    def parse_dealer_links(self,response):
        coords = response.meta['coords']
        dealers = json.loads(response.text)
        print(coords)
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
                data['url'] = "https://auto.ru/diler/cars/all/" + dealer["dealerCode"] + "/"
                yield data
         
    def start_requests(self):
        global ip;
        ip = generateIp(ip)
        spravka = generateSpavka(ip)
        cookies['spravka'] = spravka
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
        try:
            pages = response.css("a.ListingPagination__page::text").extract()[-1]
        except Exception:
            pages = 1
        link = response.url
        for page in range(1, int(pages)+1):
            global ip;
            ip = generateIp(ip)
            spravka = generateSpavka(ip)
            cookies['spravka'] = spravka
            yield Request(link + "?page=" + str(page), cookies=cookies, 
                    headers=headers, callback=self.parse_page, meta={'link':link}, dont_filter=True)

    def parse_page(self, response):
        link = response.meta['link']
        try:
            cars = response.css("a.ListingItemTitle__link::attr(href)").extract()
        except Exception:
            cars = []
        for car in cars:
            data = {}
            data['dealer link'] = link
            data['car link'] = car
            yield data
            