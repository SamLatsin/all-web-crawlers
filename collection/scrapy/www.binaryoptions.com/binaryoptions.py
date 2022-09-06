import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
import pycountry


class BinaryoptionsSpider(scrapy.Spider):
    name = 'binaryoptions'
    allowed_domains = ['www.binaryoptions.com']
    start_urls = ['https://www.binaryoptions.com/broker/']

    def parse(self, response):
        # link = "https://www.binaryoptions.com/broker/quotex/"
        # yield Request(link, callback=self.parse_broker, dont_filter=True)

        links = response.css("#main-menu > li:nth-child(3) > .megamenu:nth-child(3) > li:nth-child(1) > ul > li > a::attr(href)").extract()
        for link in links:
            yield Request(link, callback=self.parse_broker, dont_filter=True)

    def parse_broker(self, response):
        data = {}
        data['name'] = response.css(".last::text").extract_first().strip()
        pros = response.css(".col-lg-7 > div:nth-child(2) > ul:nth-child(1) > li::text").extract()
        stripped = [s.strip() for s in pros]
        pros = ",".join(stripped)
        data['pros'] = pros
        # .additional-content ul

        yield Request(response.url + "reviews", callback=self.parse_reviews, dont_filter=True, meta={'data':data})

    def parse_reviews(self, response):
        data = response.meta['data']
        titles = response.css("div.bg-white > div:nth-child(1) > div:nth-child(2) > h5:nth-child(1)::text").extract()
        texts = response.css("div.bg-white > div:nth-child(1) > div:nth-child(2)::text").extract()
        authors = response.css("div.bg-white > div:nth-child(1) > div:nth-child(1) > h5:nth-child(1)::text").extract()
        dates = response.css("div.bg-white > div:nth-child(1) > div:nth-child(1) > p:nth-child(2)::text").extract()

        for index,elem in enumerate(titles):
            if len(elem) < 5:
                titles.remove(elem)
            else:
                titles[index] = titles[index].split(":")[1].replace('"', "").strip()
                if titles[index] == "":
                    titles.remove(titles[index])

        new_texts = []
        for index,elem in enumerate(texts):
            if len(elem.strip()) > 1:
                new_texts.append(elem.strip()) 
        texts = new_texts

        reviews = []
        for index,elem in enumerate(dates):
            review = {}
            if int(elem.strip()[0:4]) >= 2020:
                review['title'] = titles[index]
                review['text'] = texts[index]
                review['author'] = authors[index]
                review['date'] = elem.strip()
                reviews.append(review)
        data['reviews'] = json.dumps(reviews)

        link = response.url.replace(response.url.split("/")[-2], "fees") 
        yield Request(link, callback=self.parse_fees, dont_filter=True, meta={'data':data})

    def parse_fees(self, response):
        data = response.meta['data']

        keys_strong = ['Deposit fees', 'Withdrawal fees', 'Trading fees']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = response.css(".table > tbody:nth-child(2) > tr > td:nth-child(1)::text").extract()
            for id,cat in enumerate(cats):
                if (cat.strip()[-1] == ":"):
                    cats[id] = cat.strip()[:-1]
                else:
                    cats[id] = cat.strip()
            cats = list(filter(None, cats))
        except Exception:
            cats = []

        values = response.css(".table > tbody:nth-child(2) > tr > td:nth-child(2)::text").extract()
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""
        link = response.url.replace(response.url.split("/")[-2], "deposit") 
        yield Request(link, callback=self.parse_deposit, dont_filter=True, meta={'data':data})

    def parse_deposit(self, response):
        data = response.meta['data']

        keys_strong = ['Minimum deposit', 'Payment methods', 'Deposit fees']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = response.css(".table > tbody:nth-child(1) > tr > td:nth-child(1)::text").extract()
            for id,cat in enumerate(cats):
                if (cat.strip()[-1] == ":"):
                    cats[id] = cat.strip()[:-1]
                else:
                    cats[id] = cat.strip()
            cats = list(filter(None, cats))
        except Exception:
            cats = []

        values = response.css(".table > tbody:nth-child(1) > tr > td:nth-child(2)::text").extract()
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""
        link = response.url.replace(response.url.split("/")[-2], "withdrawal") 
        yield Request(link, callback=self.parse_withdrawal, dont_filter=True, meta={'data':data})

    def parse_withdrawal(self, response):
        data = response.meta['data']

        keys_strong = ['Minimum withdrawal', 'Payment methods', 'Withdrawal fees', 'Withdrawal duration']
        for key in keys_strong:
            if key != 'Payment methods':
                data[key] = ""

        try:
            cats = response.css(".table > tbody:nth-child(1) > tr > td:nth-child(1)::text").extract()
            for id,cat in enumerate(cats):
                if (cat.strip()[-1] == ":"):
                    cats[id] = cat.strip()[:-1]
                else:
                    cats[id] = cat.strip()
            cats = list(filter(None, cats))
        except Exception:
            cats = []

        values = response.css(".table > tbody:nth-child(1) > tr > td:nth-child(2)::text").extract()
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    if key == 'Payment methods':
                        try:
                            data['Withdrawal methods'] = values[id].strip()
                        except Exception:
                            data['Withdrawal methods'] = ""
                    else:
                        try:
                            data[key1] = values[id].strip()
                        except Exception:
                            data[key1] = ""
        yield data















