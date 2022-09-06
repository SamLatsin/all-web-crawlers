import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
from phpserialize import *
import urllib.request

class BroCssSpider(scrapy.Spider):
    name = 'bro-css'
    allowed_domains = ['brobank.ru']
    # start_urls = ['https://brobank.ru/credit-norvikbank-zalog/']
    # start_urls = ['https://brobank.ru/credit-vuzbank/']
    # start_urls = ['https://brobank.ru/credit-alfabank/']
    # start_urls = ['https://brobank.ru/credit-gazprombank-light/']
    


    def start_requests(self):
        with open("input.txt", encoding = 'utf-8') as f:
            start_urls = [url.strip() for url in f.readlines()]
            for url in start_urls:
                yield Request(url)

    def parse(self, response):
        for lead in response.css("body"):
            data = {}
            #первая часть тз
            data['Название'] = lead.css("div.offer-home__item:nth-child(3) > a:nth-child(2) > strong:nth-child(1)::text").extract_first()
            data['Официальный сайт'] = lead.css("span.hidden-link-but-def::text").extract_first()
            # data['Официальный сайт'] = lead.css("body").extract()
            # .bank__table > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > a:nth-child(1)
            
            if data['Официальный сайт'] == "Подать заявку":
                data['Официальный сайт'] = lead.css("span.bank-offer__flex_link:nth-child(2)::text").extract_first()
            data['Ссылка на сайт'] = lead.css("span.hidden-link-but-def::attr(data-link)").extract_first()

            data['Макс сумма'] = lead.css("div.lead__item:nth-child(1) > span:nth-child(2) > strong:nth-child(1)::text").extract_first();
            data['Макс сумма'] = "".join(re.findall(r'\d+', data['Макс сумма']))

            # data['Ставка'] = lead.css("div.lead__item:nth-child(2) > span:nth-child(2) > strong:nth-child(1)::text").extract_first()
            # data['Ставка'] = data['Ставка'].replace(",", ".")
            # data['Ставка'] = re.findall(r"[-+]?\d*\.\d+|\d+", data['Ставка'])[0]
            
            data['Срок до'] = lead.css("div.lead__item:nth-child(3) > span:nth-child(2) > strong:nth-child(1)::text").extract_first()
            data['Мин сумма'] = lead.css("div.lead__item:nth-child(4) > span:nth-child(2) > strong:nth-child(1)::text").extract_first()
            data['Мин сумма'] = "".join(re.findall(r'\d+', data['Мин сумма']))

            data['Возраст заемщика'] = lead.css("div.lead__item:nth-child(5) > span:nth-child(2) > strong:nth-child(1)::text").extract_first()
            data['Решение'] = lead.css("div.lead__item:nth-child(6) > span:nth-child(2) > strong:nth-child(1)::text").extract_first()
            # вторая часть тз
            data['Лого'] = lead.css(".offer-home__item_img_bank::attr(data-src)").extract_first()
            data['logo_href'] = lead.css(".offer-home__item_img_bank::attr(data-src)").extract_first()
            data['Лого'] = lead.css(".offer-home__item_img_bank::attr(data-src)").extract_first()
            data['Лого'] = "https://carfinance.ru/files/" + re.findall('(\w+)', data['Лого'])[8] + '.' + re.findall('(\w+)', data['Лого'])[9]
            # data['Описание'] = lead.css(".article > p:nth-child(2)::text").extract_first()
            data['Описание'] = lead.css(".article").extract_first()
            # data['Описание'] = data['Описание'].re("<p>(.+):</p>\s(.+)<a")
            info = data['Описание']
            info = info[info.find("<p>"):info.find("<a class")]
            data['Описание'] = info
            

            data['Примечание'] = lead.css(".important_blue::text").extract_first()
            
            data['Телефон'] = lead.css("div.offer-home__item:nth-child(5) > a:nth-child(2)::text").extract_first()
            data['Телефон'] = "".join(re.findall(r'\d+', data['Телефон']))

            data['Почта'] = lead.css("div.offer-home__item:nth-child(6) > a:nth-child(2)::text").extract_first()

            data['Преимущества'] = lead.css(".article > ul").extract_first()
            data['Как оформить заявку'] = lead.css(".article > ul").extract()
            if (len(data['Как оформить заявку']) <= 1):
                data['Как оформить заявку'] = lead.css(".article > ol").extract_first()
            else:
                data['Как оформить заявку'] = data['Как оформить заявку'][1]
            # if lead.css(".article > h3:nth-child(4)::text").extract_first():
            #     if "преимущества" in (lead.css(".article > h3:nth-child(4)::text").extract_first().lower()):
            #         data['Преимущества'] = lead.css(".article > ul:nth-child(5) > li::text").extract()
            #         temp = ""
            #         for elem in data['Преимущества']:
            #             temp += "<p>&bull; " + elem + "</p>\n"
            #         data['Преимущества'] = temp
            # if lead.css(".article > h3:nth-child(6)::text").extract_first():
            #     if "преимущества" in (lead.css(".article > h3:nth-child(6)::text").extract_first().lower()):
            #         data['Преимущества'] = lead.css(".article > ul:nth-child(7) > li::text").extract()
            #         temp = ""
            #         for elem in data['Преимущества']:
            #             temp += "<p>&bull; " + elem + "</p>\n"
            #         data['Преимущества'] = temp

            # if lead.css(".article > h2:nth-child(8)::text").extract_first():
            #     if "кредит" in (lead.css(".article > h2:nth-child(8)::text").extract_first().lower()):
            #         data['Как оформить заявку'] = lead.css(".article > ol:nth-child(9) > li::text").extract()
            #         temp = ""
            #         for elem in data['Как оформить заявку']:
            #             temp += "<p>" + elem + "</p>\n"
            #         data['Как оформить заявку'] = temp
            # if lead.css(".article > h2:nth-child(10)::text").extract_first():
            #     if "кредит" in (lead.css(".article > h2:nth-child(10)::text").extract_first().lower()):
            #         data['Как оформить заявку'] = lead.css(".article > ol:nth-child(12) > li::text").extract()
            #         temp = ""
            #         for elem in data['Как оформить заявку']:
            #             temp += "<p>" + elem + "</p>\n"
            #         data['Как оформить заявку'] = temp
            data['Способы пополнения'] = lead.css("tr > td:nth-child(1) > div:nth-child(1) > span:nth-child(3)::text").extract()
            data['Способы пополнения'] = ", ".join(data['Способы пополнения'])
            url = lead.css("div.menu__block > a:nth-child(2)::attr(href)").extract_first()
            yield Request(url, callback=self.parse_tariffs, meta={'data': data})

    def parse_tariffs(self, response):
        data = response.meta.get('data')
        # data['Максимальная сумма кредита'] = response.css(".tariffs__table > tr:nth-child(1) > td:nth-child(2)::text").extract_first()
        # data['Минимальная сумма кредита'] = response.css(".tariffs__table > tr:nth-child(2) > td:nth-child(2)").extract_first()
        # data['Минимальная сумма кредита'] = "".join(re.findall(r'\d+', data['Минимальная сумма кредита']))
        data['Срок кредита'] = response.css(".tariffs__table > tr:nth-child(3) > td:nth-child(2)::text").extract_first()
        data['Минимальный процент'] = response.css(".tariffs__table > tr:nth-child(4) > td:nth-child(2)::text").extract_first()
        data['Минимальный процент'] = data['Минимальный процент'].replace(",", ".")
        try:
            data['Минимальный процент'] = re.findall(r"[-+]?\d*\.\d+|\d+", data['Минимальный процент'])[0]
        except:
            data['Минимальный процент'] = ""
        data['Максимальный процент'] = response.css(".tariffs__table > tr:nth-child(4) > td:nth-child(2)::text").extract_first()
        data['Максимальный процент'] = data['Максимальный процент'].replace(",", ".")
        try:
            data['Максимальный процент'] = re.findall(r"[-+]?\d*\.\d+|\d+", data['Максимальный процент'])[1]
        except:
            data['Максимальный процент'] = ""
        data['Цель кредита'] = response.css(".tariffs__table > tr:nth-child(5) > td:nth-child(2)::text").extract_first()
        data['Подача заявки'] = response.css(".tariffs__table > tr:nth-child(6) > td:nth-child(2)::text").extract_first()
        # data['Решение по кредиту'] = response.css(".tariffs__table > tr:nth-child(7) > td:nth-child(2)::text").extract_first()
        data['Справки о доходе'] = response.css(".tariffs__table > tr:nth-child(8) > td:nth-child(2)::text").extract_first()
        # data['Возраст'] = response.css(".tariffs__table > tr:nth-child(9) > td:nth-child(2)::text").extract_first()
        data['Кредитная история'] = response.css(".tariffs__table > tr:nth-child(10) > td:nth-child(2)::text").extract_first()
        data['Страхование'] = response.css(".tariffs__table > tr:nth-child(11) > td:nth-child(2)::text").extract_first()
        data['Прописка в регионе банка'] = response.css(".tariffs__table > tr:nth-child(12) > td:nth-child(2)::text").extract_first()
        data['Способы получения'] = response.css(".tariffs__table > tr:nth-child(13) > td:nth-child(2)::text").extract_first()
        data['Способы погашения'] = response.css(".tariffs__table > tr:nth-child(14) > td:nth-child(2)::text").extract_first()
        data['Залог'] = response.css(".tariffs__table > tr:nth-child(15) > td:nth-child(2)::text").extract_first()
        data['Поручительство'] = response.css(".tariffs__table > tr:nth-child(16) > td:nth-child(2)::text").extract_first()
        data['Пеня при просрочке'] = response.css(".tariffs__table > tr:nth-child(17) > td:nth-child(2)::text").extract_first()
        names = response.css("div.documents__item > a::text").extract()
        for index,item in enumerate(names):
            names[index] = names[index].strip()
        for index,item in enumerate(names):
            names.remove('')
        hrefs = response.css("div.documents__item > a::attr(href)").extract()
        data['Документы'] = ""
        for index,item in enumerate(hrefs):
            data['Документы'] += names[index] + ":" + hrefs[index] + ";" 
        yield data