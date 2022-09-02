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

class EvolveSpider(scrapy.Spider):
    name = 'evolve'
    allowed_domains = ['evolve.ae']
    start_urls = ["https://evolve.ae/brand"]

    def parse(self, response):
        brands = response.css(".ev_brands-list  .item::attr(href)").extract()
        for brand in brands:
            yield Request(brand, callback=self.parse_brand, meta={'page':1, 'link': brand})

    def parse_brand(self, response):
        arrows = response.css(".pagination-link-next::text").extract()
        page = response.meta['page']
        cars = response.css(".car_item > a::attr(href)").extract()
        for car in cars:
            yield Request(car, callback=self.parse_car)     
        for arrow in arrows:
            if arrow == "»":
                yield Request(response.meta['link'] + "?page=" + str(page + 1), callback=self.parse_brand, meta={'page':page + 1, 'link': response.meta['link']})     

    def parse_car(self, response):
        data = {}
        data['url'] = response.request.url
        bread = response.css(".ev_breadcrumbs a::text").extract()
        data['mark'] = bread[2].strip()
        try:
            data['model'] = bread[3].strip()
        except Exception:
            data['model'] = ""
        data['equipment'] = response.css(".ev_breadcrumbs span::text").extract_first().strip()
        data['imgs'] = ""
        data['imgs_links'] = ""
        photo_links = response.css(".car-gallery > a::attr(href)").extract()
        for link in photo_links: # https://evolve.ae/uploads/car/photo/m/ + link
            data['imgs_links'] += link + ","
            photo = link.split("/")[-1]
            data['imgs'] += photo + ","
        if data['imgs'] != "":
            main_photo = response.css(".car-main-photo::attr(href)").extract_first()
            data['imgs_links'] = main_photo + "," + data['imgs_links']
            data['imgs_links'] = data['imgs_links'][:-1]
            data['imgs'] = main_photo.split("/")[-1] + "," + data['imgs']
            data['imgs'] = data['imgs'][:-1]
        else:
            main_photo = response.css(".car-main-photo::attr(href)").extract_first()
            if main_photo:
                data['imgs_links'] = main_photo
                data['imgs'] = main_photo.split("/")[-1]
        yield data









