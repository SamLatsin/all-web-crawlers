import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import re
import urllib.request
import math
import json
from urllib import parse

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

class OneclickdriveSpider(scrapy.Spider):
    name = 'oneclickdrive_cars'
    allowed_domains = ['www.oneclickdrive.com']
    start_urls = ['https://www.oneclickdrive.com/rent-a-car-dubai']

    def parse(self, response):
        # yield Request("https://www.oneclickdrive.com/details/index/search-car-rentals-dubai/Mercedes-Benz/AMG-G63/?id=9778", callback=self.parse_car, dont_filter=True)
        # yield Request("https://www.oneclickdrive.com/details/index/search-car-rentals-dubai/Nissan/Kicks/?id=7578", callback=self.parse_car, dont_filter=True)
        # yield Request("https://www.oneclickdrive.com/details/index/search-car-rentals-dubai/Audi/A6/?id=13153", callback=self.parse_car, dont_filter=True)
        count = response.css("#hidfilter::text").extract_first()
        count = get_numbers(count)
        count = math.ceil(float(count[2]) / float(count[1]))
        for i in range(1,count + 1):
            yield Request("https://www.oneclickdrive.com/rent-a-car-dubai?order=featured&page=" + str(i), callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):
        car_links = response.css("a.col-md-8.m-t-15::attr(href)").extract()
        for car_link in car_links:
            yield Request(car_link, callback=self.parse_car, dont_filter=True)

    def parse_car(self, response):
        data = {}
        data["url"] = response.url
        bread = response.css(".breadcrumb > div > a:nth-child(1) > span:nth-child(1)::text").extract()
        # data["name"] = bread[-2].strip() + " " + bread[-1].strip()
        data["mark"] = bread[-2].strip()
        data["model"] = bread[-1].strip()
            
        data["year"] = get_numbers(response.css(".dsktit::text").extract_first())[-1]
        imgs = response.css("img.imagegal::attr(src)").extract()
        data["imgs"] = []
        data["imgs_links"] = []
        if imgs:
            for img in imgs:
                data["imgs"].append(img.split("/")[-1].split("?")[0])
            data["imgs"] = ",".join(data["imgs"])
            data["imgs_links"] = ",".join(imgs)
        else:
            img = response.css("img.singleslid::attr(src)").extract_first()
            data["imgs"] = img.split("/")[-1].split("?")[0]
            data["imgs_links"] = img
        skill_box = response.css("span.info-d::text").extract()
        for skill in skill_box:
            skill = skill.strip()
            if "Insurance included" in skill:
                data["insurance"] = 1
            if "Deposit" in skill:
                data["deposit"] = get_numbers(skill)[-1]
            if "Free Delivery" in skill:
                data["free_delivery"] = 1
        if "free_delivery" not in data:
            data["free_delivery"] = 0
        if "deposit" not in data:
            data["deposit"] = ""
        if "insurance" not in data:
            data["insurance"] = 0

        data["price_day"] = ""
        data["price_month"] = ""
        data["price_week"] = ""
        data["mileage_day"] = ""
        data["mileage_month"] = ""
        data["mileage_week"] = ""

        rows = response.css(".price-table .pricboxdt")
        for row in rows:
            elements = row.css("td::text").extract()
            elements = [x for x in elements if x.strip()]
            for index,elem in enumerate(elements):
                if "Day" in elem:
                    data["price_day"] = "".join(get_numbers(elements[index+2])) 
                    data["mileage_day"] = "".join(get_numbers(elements[index+1])) 
                if "Week" in elem:
                    data["price_week"] = "".join(get_numbers(elements[index+2])) 
                    data["mileage_week"] = "".join(get_numbers(elements[index+1])) 
                if "Month" in elem:
                    data["price_month"] = "".join(get_numbers(elements[index+2])) 
                    data["mileage_month"] = "".join(get_numbers(elements[index+1])) 

        spans = response.css("div.cardetaillist > div > span::text").extract()
        data["insurance_type"] = ""
        data["cdw_insurance"] = ""
        data["additional_driver_insurance"] = ""
        data["additional_mileage_charge"] = ""
        data["salik_charges"] = ""
        data["min_driver_age"] = ""
        for index,span in enumerate(spans):
            if "Insurance" in span:
                data["insurance_type"] = spans[index+1].strip()
            if "CDW Insurance" in span:
                data["cdw_insurance"] = spans[index+1].strip()
            if "Additional driver insurance" in span:
                data["additional_driver_insurance"] = spans[index+1].strip()
            if "Additional mileage charge" in span:
                data["additional_mileage_charge"] = spans[index+1].strip()
            if "Salik / Toll Charges" in span:
                data["salik_charges"] = spans[index+1].strip()
            if "Driver's Age" in span:
                data["min_driver_age"] = spans[index+1].strip()

        data["exterior_colors"] = []
        exterior_colors = response.css("div.cardetaillist:nth-child(2) > div:nth-child(4) > span:nth-child(2) > span:nth-child(2) > span").extract()
        if exterior_colors:
            for index,color in enumerate(exterior_colors):
                colors = {}
                color_name = color[color.find("available in") + 12:color.find("color")].strip()
                color_hex = color[color.find("fill:") + 5:color.find(";stroke")].strip()
                colors["name"] = color_name
                colors["hex"] = color_hex
                data["exterior_colors"].append(colors)
            data["exterior_colors"] = json.dumps(data["exterior_colors"])

            data["interior_colors"] = []

            interior_colors = response.css("div.cardetaillist:nth-child(2) > div:nth-child(5) > span:nth-child(2) > span:nth-child(2) > span").extract()
            for index,color in enumerate(interior_colors):
                colors = {}
                color_name = color[color.find("available in")+12:color.find("color")].strip()
                color_hex = color[color.find("fill:") + 5:color.find(";stroke")].strip()
                colors["name"] = color_name
                colors["hex"] = color_hex
                data["interior_colors"].append(colors)
            data["interior_colors"] = json.dumps(data["interior_colors"])
        else:
            data["interior_colors"] = ""
            data["exterior_colors"] = []
            exterior_colors = response.css("div.cardetaillist:nth-child(2) > div:nth-child(4) > span:nth-child(2) > span").extract()
            for index,color in enumerate(exterior_colors):
                colors = {}
                color_name = color[color.find("available in") + 12:color.find("color")].strip()
                color_hex = color[color.find("fill:") + 5:color.find(";stroke")].strip()
                colors["name"] = color_name
                colors["hex"] = color_hex
                data["exterior_colors"].append(colors)
            data["exterior_colors"] = json.dumps(data["exterior_colors"])

        car_specs_imgs = response.css("div.row:nth-child(6) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li > img::attr(src)").extract()
        car_specs_names_raw = response.css("div.row:nth-child(6) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li::text").extract()
        car_specs_names = []
        car_specs = []
        for name in car_specs_names_raw:
            if name.strip() and name.strip() != "View More":
                car_specs_names.append(name.strip())
        for index,name in enumerate(car_specs_names):
            spec = {}
            spec["name"] = name
            spec["img"] = car_specs_imgs[index].split("/")[-1].split("?")[0]
            car_specs.append(spec)
        data["car_specs"] = json.dumps(car_specs)
        data["car_specs_imgs_to_download"] = ",".join(car_specs_imgs)

        # car_features_raw = response.css("ul.fespecbox:nth-child(4) > li::text").extract()
        car_features_raw = response.css("div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > ul:nth-child(1) > li::text").extract()
        car_features = []
        for name in car_features_raw:
            if name.strip() and name.strip() != "View More":
                car_features.append(name.strip())
        data["features"] = ",".join(car_features)

        faqs = []
        questions = response.css("div.faqbottom > button > h3::text").extract()
        answers = response.css("div.faqbottom > div > div::text").extract()
        for index, question in enumerate(questions):
            faq = {}
            faq["question"] = question.strip().replace("  ", "").replace("\n", "")
            faq["answer"] = answers[index].strip().replace("  ", "").replace("\n", "")
            faqs.append(faq)
        data["faq"] = json.dumps(faqs)

        data["partner_name"] = response.css("#comname::text").extract_first().strip()
        data["partner_logo_link"] = response.css(".cmpbrndlogo::attr(src)").extract_first().strip()
        data["partner_logo"] = data["partner_logo_link"].split("/")[-1].split("?")[0]

        partner_about = response.css("#openModal4 > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > div:nth-child(2)::text").extract_first().strip()
        data["partner_year"] = ""
        numbers = get_numbers(partner_about)
        for number in numbers:
            if int(number) > 1800 and int(number) < 2030:
                data["partner_year"] = number

        try:
            data["work_hours"] = response.css("span.text-right:nth-child(1)::text").extract_first().strip()
        except Exception:
            data["work_hours"] = response.css(".timebar > span:nth-child(2)::text").extract_first().strip()

        data["partner_address"] = response.css(".addressbox::text").extract()[1].strip()

        elements = response.css(".card-body > *::text").extract()
        keywords = []
        for element in elements:
            if element.strip():
                keywords.append(element.strip())

        data["partner_branch_locations"] = []
        data["partner_payment_mode"] = []
        data["partner_car_fleet"] = []

        for index,keyword in enumerate(keywords):
            if keyword == "Branch Location(s)":
                i = index
                while not (keywords[i+1] == "Fast Delivery Locations" or keywords[i+1] == "Car Fleet" or keywords[i+1] == "Listed in"):
                    data["partner_branch_locations"].append(keywords[i + 1])
                    i += 1
            if keyword == "Payment Mode":
                i = index
                while not (keywords[i+1] == "Fast Delivery Locations" or keywords[i+1] == "Car Fleet" or keywords[i+1] == "Listed in"):
                    data["partner_payment_mode"].append(keywords[i + 1])
                    i += 1
            if keyword == "Car Fleet":
                i = index
                while not (keywords[i+1] == "Fast Delivery Locations" or keywords[i+1] == "Car Fleet" or keywords[i+1] == "Listed in"):
                    data["partner_car_fleet"].append(keywords[i + 1])
                    i += 1

                
        data["partner_branch_locations"] = ",".join(data["partner_branch_locations"])
        data["partner_payment_mode"] = ",".join(data["partner_payment_mode"])
        data["partner_car_fleet"] = ",".join(data["partner_car_fleet"])
        data["partner_fast_delivery_locations"] = ",".join(response.css(".modal-body > div > a.rightbarbtn::text").extract())

        data["partner_rating"] = response.css("span[itemprop='ratingValue']::text").extract_first().strip()

        data["category"] = bread[0]
        data["phone"] = "".join(get_numbers(response.css("#mobhideconct > a:nth-child(1) > span:nth-child(2)::text").extract_first()))
        data["seats"] = ""

        specs = response.css(".fespecbox > li::text").extract()
        for spec in specs:
            if "Passengers" in spec:
                data["seats"] = get_numbers(spec)[0]

        tags = response.css(".btnspec > button::text").extract()
        data["tags"] = []
        for tag in tags:
            data["tags"].append(tag.strip())

        data["tags"] = ",".join(data["tags"])

        url = response.url
        car_id = parse.parse_qs(parse.urlparse(url).query)['id'][0]

        params = {
            'car_id': car_id,
            'emirate': 'Dubai',
            'rate': '1',
            'default_emirate': 'Dubai',
            'currency_redirect_and': '',
            'lang_anchor': 'https://www.oneclickdrive.com',
            'lang_code': 'en',
            'currency': 'AED',
            'redirect_url': '/details',
        }
        yield scrapy.FormRequest('https://www.oneclickdrive.com/details/similar_cars', callback=self.parse_similar,
                                     method='POST', formdata=params, meta={'data':data})

    def parse_similar(seld, response):
        data = response.meta["data"]

        similar = response.css("a::attr(href)").extract()
        data["similar"] = []
        for link in similar:
            if "?id=" in link:
                data["similar"].append(link)
        data["similar"] = set(data["similar"])
        data["similar"] = ",".join(data["similar"])

        data['name'] = data["mark"] + " " + data["model"]
        data['slug'] = "-".join(data["name"].lower().split(" "))
        data['markSlug'] = "-".join(data["mark"].lower().split(" "))
        data['modelSlug'] = "-".join(data["model"].lower().split(" "))
        yield data








