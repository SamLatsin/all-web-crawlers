import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request

class CreditznatokSpider(scrapy.Spider):
    name = 'creditznatok'
    allowed_domains = ['creditznatok.ru']
    # start_urls = ["https://creditznatok.ru/avtokredity/vtb/bank-vtb-avtokredit-na-novyj-avtomobil/"]

    def start_requests(self):
        with open("./../links input/creditznatok-input.csv", encoding = 'utf-8') as f:
            start_urls = [url.strip() for url in f.readlines()]
            start_urls = start_urls[1:]
            for url in start_urls:
                yield Request(url)

    def parse(self, response):
        for bank in response.css("body"):
            data = {}
            data['url'] = response.request.url
            name_and_credit = bank.css(".comments-title > div:nth-child(1) > div:nth-child(1) > h1:nth-child(1)::text").extract_first()
            data['Название банка'] = ""
            data['Название кредита'] = ""
            # print(name_and_credit.split(" — "))
            # print(name_and_credit.find('\u2013'))
            # u'\u2e23'
            if (name_and_credit.find(u'\u2014') != -1):
                data['Название банка'] = name_and_credit.split(u'\u2014')[0].strip()
                data['Название кредита'] = name_and_credit.split(u'\u2014')[1].strip()
            if (name_and_credit.find('\u2013') != -1):
                data['Название банка'] = name_and_credit.split('\u2013')[0].strip()
                data['Название кредита'] = name_and_credit.split('\u2013')[1].strip()
            
            data["Лицензия"] = bank.css("div.ad_obmen__sidebar-bank--item:nth-child(3) > div:nth-child(2)::text").extract_first()
            ogrn = bank.css(".typo-4").extract_first()
            if ogrn:
                data["ОГРН"] = ogrn[ogrn.find("ОГРН: ") + 6 : ogrn.find("</span>")]
            else:
                data["ОГРН"] = ""
            if (data["ОГРН"] == ' class="typo-4 cl-4">Лицензия: 1000'):
                data["ОГРН"] = ""

            keys   = bank.css("div.product__tab--line > div:nth-child(1)::text").extract()
            values = bank.css("div.product__tab--line > div:nth-child(2)").extract()
            for id, value in enumerate(values):
                values[id] = value[ value.find("\">") + 2: value.find("</div>")]

            data['Сумма'] =                                  ""
            data['Процентная ставка'] =                      ""
            data['Срок'] =                                   ""
            data['Возраст'] =                                ""
            data['Минимальный взнос'] =                      ""
            data['Продавец'] =                               ""
            data['Вид транспортного средства'] =             ""
            data['Тип транспортного средства'] =             ""
            data['Возраст транспортного средства'] =         ""
            data['Мораторий на досрочное погашение'] =       ""
            data['Штраф за досрочное погашение'] =           ""
            data['Необходимость страхования'] =              ""
            data['Подтверждение дохода'] =                   ""
            data['Регистрация по месту получения кредита'] = ""
            for id, key in enumerate(keys):
                if (key == "Сумма"):
                    data['Сумма'] = values[id]
                if (key == "Процентная ставка"):
                    data['Процентная ставка'] = values[id]
                if (key == "Срок"):
                    data['Срок'] = values[id]
                if (key == "Возраст"):
                    data['Возраст'] = values[id]
                if (key == "Минимальный взнос"):
                    data['Минимальный взнос'] = values[id]
                if (key == "Продавец"):
                    data['Продавец'] = values[id]
                if (key == "Вид транспортного средства"):
                    data['Вид транспортного средства'] = values[id]
                if (key == "Тип транспортного средства"):
                    data['Тип транспортного средства'] = values[id]
                if (key == "Возраст транспортного средства"):
                    data['Возраст транспортного средства'] = values[id]
                if (key == "Мораторий на досрочное погашение"):
                    data['Мораторий на досрочное погашение'] = values[id]
                if (key == "Штраф за досрочное погашение"):
                    if ( values[id] == '<i class="cz-icon cz-yes"></i>'):
                        data['Штраф за досрочное погашение'] = "Да"
                    else:
                        data['Штраф за досрочное погашение'] = values[id]
                if (key == "Необходимость страхования"):
                    data['Необходимость страхования'] = values[id]
                if (key == "Подтверждение дохода"):
                    if ( values[id] == '<i class="cz-icon cz-yes"></i>'):
                        data['Подтверждение дохода'] = "Да"
                    else:
                        data['Подтверждение дохода'] = values[id]
                if (key == "Регистрация по месту получения кредита"):
                    data['Регистрация по месту получения кредита'] = values[id]

            data['Особенности'] = ""
            keys = bank.css("div.product__card--item > div:nth-child(1) > span:nth-child(2)::text").extract()
            values = bank.css("div.product__card--item > div:nth-child(2)").extract()
            for id, key in enumerate(keys):
                # print(key)
                if (key == "Особенности"):
                    elems = values[id].split(",")
                    for elem in elems:
                        data['Особенности'] += elem[elem.find("/\">") + 3 : elem.find("</a>")] + ","

            data['Рекомендуемые предложения'] = ""
            elems = bank.css("div.similar-row > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)::attr(href)").extract()
            for elem in elems:
                data['Рекомендуемые предложения'] += elem + ","
                
            data['img-href'] = bank.css(".product__card--logo > a:nth-child(1) > img:nth-child(1)::attr(data-lazy-src)").extract_first();
            data['img'] = "https://fininspector.ru/files/" + bank.css(".product__card--logo > a:nth-child(1) > img:nth-child(1)::attr(data-lazy-src)").extract_first().split("/")[-1];
            yield data

            