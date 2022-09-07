import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
from scrapy.http import HtmlResponse

stop_words = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "%", "?"
]

start_links = [
    "https://kinsta.com/blog/ipv4-vs-ipv6/",
    "https://www.dnsstuff.com/what-is-network-topology", 
    "https://afteracademy.com/blog/what-is-network-topology-and-types-of-network-topology",
    "https://www.studytonight.com/computer-networks/network-topology-types",
    "https://phoenixnap.com/blog/ipv4-vs-ipv6"
]

domains = [
    "kinsta.com", 
    "www.dnsstuff.com", 
    "afteracademy.com",
    "www.studytonight.com",
    "phoenixnap.com"
]

class VpnsSpider(scrapy.Spider):
    name = 'vpns'
    allowed_domains = domains

    def start_requests(self):
        for link in start_links:
            yield Request(url=link, callback=self.parse_links)

    def parse_links(self, response):
        links = response.css("a::attr(href)").extract()
        for link in links:
            if link.find("https://") != -1:
                yield Request(url=link, callback=self.parse_sentences)

    def parse_sentences(seelf, response):
        texts = response.css("p::text").extract()
        for text in texts:
            text = text.strip()
            if text.find(".") != -1 and text[-1] == ".":
                sentences = text.split(".")
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and sentence[0].isupper() and sentence[-1] != "," and sentence[-1] != ":" and sentence[-1] != "…" and len(sentence.split(" ")) > 5:
                        if not any(word in stop_words for word in sentence):
                            data = {}
                            data['sentence'] = sentence
                            yield data
