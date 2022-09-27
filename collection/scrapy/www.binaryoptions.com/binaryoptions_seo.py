import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json


class BinaryoptionsSpider(scrapy.Spider):
    name = 'binaryoptions_seo'
    allowed_domains = ['www.binaryoptions.com']
    start_urls = ['https://www.binaryoptions.com/']

    def __init__(self):
        self.filter=["/id/", "/pt/", "/tr/", "/ru/", "/ms/", "/es/", "/fr/", "/it/", 
                     "/uk/", "/ka/", "/bg/", "/cs/", "/da/", "/de/", "/el/", "/et/", 
                     "/fi/", "/hu/", "/nb/", "/pl/", "/sv/", "/sr/", "/ro/", "/co/",
                     "/mx/", "/es_ar/", "/ve/", "/az/", "/hr/", "/nl/", "/sk/", "/lt/", 
                     "/th/", "/vi/", "/ko/", "/ja/", "/ar/", "/za/", "/ur/", "/do/",
                     "/pe/", "/pt_pt/", "/bn/", "/ta/", "/lk/", "/cl/", "/ec/", "/sw/",
                     "/hk/", "/cn/", "/tw/", "/be/", "/am/", "/af/", "/kk/", "/ceb/", 
                     "/uy/", "/fa/", "/sq/", "/uz/", "/lv/", "/sl/", "/au/", "/ca/",
                     "/hi/", "/cr/", "/gt/", "/pr/", "/ch/", "/at/"]

    def parse(self, response):
        data = {}
        data["url"] = response.url
        data["h1"] = response.css("h1::text").extract_first()
        data["title"] = response.css('head > title::text').extract_first()
        data["description"] = response.xpath("//meta[@name='description']/@content").extract_first()

        for href in response.css('a::attr(href)').extract():
            if not any(country in href for country in self.filter):
                yield response.follow(href, self.parse)

        yield data