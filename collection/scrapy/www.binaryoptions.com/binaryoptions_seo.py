import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
import pycountry


class BinaryoptionsSpider(scrapy.Spider):
    name = 'binaryoptions_seo'
    allowed_domains = ['www.binaryoptions.com']
    start_urls = ['https://www.binaryoptions.com/']

    # def __init__(self):
    #     self.links=[]

    def parse(self, response):
        # self.links.append(response.url)
        data = {}
        data["url"] = response.url
        data["h1"] = response.css("h1::text").extract_first()
        data["title"] = response.css('head > title::text').extract_first()
        data["description"] = response.xpath("//meta[@name='description']/@content").extract_first()

        for href in response.css('a::attr(href)'):
            yield response.follow(href, self.parse)

        yield data