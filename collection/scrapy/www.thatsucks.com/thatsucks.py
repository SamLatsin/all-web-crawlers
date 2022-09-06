import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
import pycountry

class ThatsucksSpider(scrapy.Spider):
    name = 'thatsucks'
    allowed_domains = ['www.thatsucks.com']

    def start_requests(self):
        with open("./sucks_input.txt", encoding = 'utf-8') as f:
            start_urls = [url.strip() for url in f.readlines()]
            # start_urls = start_urls[0]
            # yield Request(start_urls, callback=self.parse)
            for url in start_urls:
                yield Request(url, callback=self.parse)

    def parse(self, response):
        data = {}
        keys_strong = ['Broker Name', 'Platform', 'Founded', 'Return/Refund', 'No. Of Assets', 'Regulated', 'Demo Account']
        for key in keys_strong:
            data[key] = ""

        try:
            cats = response.css(".review_broker_details tr > td:nth-child(1)::text").extract()
            for id,cat in enumerate(cats):
                if (cat.strip()[-1] == ":"):
                    cats[id] = cat.strip()[:-1]
                else:
                    cats[id] = cat.strip()
            cats = list(filter(None, cats))
            cats.remove('Bonus')
        except Exception:
            cats = []

        values = response.css(".review_broker_details tr > td:nth-child(2)::text").extract()
        for id,key in enumerate(cats):
            for key1 in keys_strong:
                if (key == key1):
                    try:
                        data[key1] = values[id].strip()
                    except Exception:
                        data[key1] = ""

        try:
            data['Bonus'] = response.css(".review_broker_details tr > td:nth-child(2) > span::text").extract_first().strip()
        except Exception:
            data['Bonus'] = ""
        try:
            data['Rating'] = response.css(".rating::text").extract_first().strip()
            data['Rating'] = data['Rating'].split('/')[0]
        except Exception:
            data['Rating'] = "closed"

        try:
            temp = []
            all_text = response.css("article > section > p::text").extract()
            stripped = [s.strip() for s in all_text]
            all_text = " ".join(stripped)
            for country in pycountry.countries:
                if country.name in all_text:
                    temp.append(country.name)
            temp = set(temp)
            data['Countries'] = ",".join(temp)   
        except Exception as e:
            print(e)
            data['Countries'] = ""

        try:
            dates_raw = response.css("div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong:nth-child(1)::text").extract()
            dates = []
            for index,date in enumerate(dates_raw):
                if len(date.strip()) == 10:
                    dates.append(date.strip() + " " + dates_raw[index+1].strip())
            names = response.css("div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > cite:nth-child(1)::text").extract()
            texts = response.css("div:nth-child(1) > div:nth-child(3) > p:nth-child(1)::text").extract()
            titles = response.css(".comment-title::text").extract()
            reviews = []
            for index,date in enumerate(dates):
                year = date[6:10]
                review = {}
                if (int(year) >= 2020):
                    review['title'] = titles[index].strip()
                    review['author'] = names[index].strip()
                    review['text'] = texts[index].strip()
                    review['date'] = dates[index].strip()
                    reviews.append(review)
            data['reviews'] = json.dumps(reviews)
        except Exception:
            data['reviews'] = ""
        yield data











