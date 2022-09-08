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

class OneclickdriveSpider(scrapy.Spider):
    name = 'oneclickdrive_brands'
    allowed_domains = ['www.oneclickdrive.com']
    start_urls = ['https://www.oneclickdrive.com/brands']

    def parse(self, response):
        data = {}
        brands = response.css("h5.item_car_brand_text_name::text").extract()
        imgs = response.css(".brand_image > img.item_car_brand_img::attr(src)").extract()
        counts = response.css(".item_car_brand_text_name > span::text").extract()
        for index, brand in enumerate(brands):
            data["brand"] = brand.strip()
            data["img"] = imgs[index]
            data["count"] = get_numbers(counts[index])[0]
            yield data
