import re
import urllib.request
import math
import json
import numpy as np
import urllib
import requests
import csv

file_name = "reviews.csv"

csrfToken = "ee6ffb6017d8a78c885cd913b1eb6459083438df:1638880502"
sessionId = "1638880502237_904492"
spn = "0.328216552734375,0.1388288071479451"
parent_reqid = "1638782722495005-2525348489-sas1-6045-sas-addrs-nmeta-new-8031"
test_buckets = "467397,0,18;204306,0,52;460256,0,39;462198,0,61;464947,0,70;467285,0,77"

sessionIdCookie = "3:1638782655.5.0.1634313571752:_vZcAg:2.1|1476760738.-1.0.1:301428837|3:244715.392860.kfyv2G4L6-DZGXv0qqU_hP5uSFg"
yandexuid = "3681872781632383078"

x_cmnt_api_key = "f748bf5f-6e7e-45c8-b380-bb504fc1e683"

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

def generate_s(string):
    n = 5381
    for r in range(0,len(string)):
        n = np.int32(33 * n ^ ord(string[r]))
    if n > 0:
        return n
    else:
        return 4294967296 + n

def parse_subcomment(reviewId):
	cookies = {
	    'yandexuid': yandexuid,
	    'Session_id': sessionIdCookie,
	}
	headers = {
	    'X-Cmnt-Api-Key': x_cmnt_api_key,
	}
	params = (
	    ('stats', '{"l":"ru","m":"wide","r":"17.0.2","s":"ugc_maps","t":"maps","v":"2.25.0","dnt":"1"}'),
	    ('order', 'time'),
	    ('entityId', reviewId),
	    ('supplierServiceSlug', 'ugc'),
	)
	response = requests.get('https://yandex.ru/comments/api/v1/tree', headers=headers, params=params, cookies=cookies)
	subcomments = json.loads(response.text)
	subcomments = subcomments['tree']
	for subcomment in subcomments:
		if subcomment != 0 and "isOfficial" in subcomments[subcomment]:
			return subcomments[subcomment]['content'][0]['text']

def parse_comments(data, count, salon_id):
	print("Starting parsing comments...")
	requests_count = math.ceil(count/50)
	# # test
	requests_count = 2
	for page in range(1, requests_count+1):
		print("Parsing page", page, "from", requests_count)
		params = {
		    "ajax": "1",
		    "businessId": salon_id,
		    "csrfToken": csrfToken,
		    "lang": "ru",
		    "page": page,
		    "pageSize": 50,
		    "ranking": "by_relevance_org",
		    "reqId": parent_reqid,
		    "sessionId": sessionId,
		}
		x = {}
		for key in sorted(params):
		    x[key] = params[key]
		params = x
		stringify = urllib.parse.urlencode(params)
		s = generate_s(stringify)
		cookies = {
		    'yandexuid': yandexuid,
		    'Session_id': sessionIdCookie,
		}
		headers = {
		}
		params = (
		    ('ajax', '1'),
		    ('businessId', salon_id),
		    ('csrfToken', csrfToken),
		    ('lang', 'ru'),
		    ('page', page),
		    ('pageSize', '50'),
		    ('ranking', 'by_relevance_org'),
		    ('reqId', parent_reqid),
		    ('s', s),
		    ('sessionId', sessionId),
		)
		response = requests.get('https://yandex.ru/maps/api/business/fetchReviews', headers=headers, params=params, cookies=cookies)
		comments = json.loads(response.text)
		i = 1
		try:
			for comment in comments['data']['reviews']:
				print("Parsing comment", i, "from", len(comments['data']['reviews']))
				i += 1
				try:
					data['Аватарка автора'] = comment['author']['avatarUrl'].replace("{size}","islands-75")
				except Exception:
					data['Аватарка автора'] = ""
				try:
					data['Имя'] = comment['author']['name']
				except:
					data['Имя'] = ""
				data['Рейтинг'] = comment['rating']
				data['Текст отзыва'] = comment['text']
				data['Дата отзыва'] = comment['updatedTime']
				data['Лайки'] = comment['reactions']['likes']
				data['Дизлайки'] = comment['reactions']['dislikes']
				data['Фото отзыва'] = ""
				photos = comment['photos']
				for photo in photos:
					data['Фото отзыва'] += photo['urlTemplate'].replace("{size}", "XXXL") + ","
				if data['Фото отзыва'] != "":
					data['Фото отзыва'] = data['Фото отзыва'][:-1]
				data['Официальный ответ'] = ""
				if comment['hasComments']:
					data['Официальный ответ'] = parse_subcomment(comment['reviewId'])
				
				with open(file_name, 'a') as f:
					w = csv.DictWriter(f, data.keys())
					w.writerow(data)
				# print(data)
		except Exception as e:
			print(str(e))

def parse_salon(meta, response):
	salon = json.loads(response.text)
	salon = salon['data']['items'][0]
	data = meta
	salon_id = salon['id'] 
	data['Название салона донора'] = salon['shortTitle']
	data['Общий рейтинг салона'] = salon['ratingData']['ratingValue']
	try:
		data['Телефон салона'] = ""
		for phone in salon['phones']:
			ph = "".join(get_numbers(phone['number']))
			ph = '8' + ph[1:]
			data['Телефон салона'] += ph + ','
		if data['Телефон салона'] != "":
			data['Телефон салона'] = data['Телефон салона'][:-1]
	except Exception as e:
		data['Телефон салона'] = ""
	data['Адрес салона'] = salon['fullAddress']
	try:
		data['Официальный сайт'] = salon['urls'][0].replace("?utm_medium=sprav&utm_source=Yandex_sprav_atdrv_YAS_jaguar_cross", "")
	except Exception as e:
		data['Официальный сайт'] = ""
	data['Прочее'] = ""
	data['Виды работ'] = ""
	data['Автострахование'] = ""
	data['Способ оплаты'] = ""
	data['Продажа автомобилей'] = ""
	data['Акции'] = ""
	for feature in salon['features']:
		if feature['type'] == "bool":
			data['Прочее'] += feature['name'].replace(",", ";") + ","
		if feature['id'] == "auto_insurance_type":
			for value in feature['value']:
				 data['Автострахование'] += value['name'].replace(",", ";") + ","
		if feature['id'] == "car_repairs":
			for value in feature['value']:
				 data['Виды работ'] += value['name'].replace(",", ";") + ","
		if feature['id'] == "payment_method":
			for value in feature['value']:
				 data['Способ оплаты'] += value['name'].replace(",", ";") + ","
		if feature['id'] == "auto_sales":
			for value in feature['value']:
				 data['Продажа автомобилей'] += value['name'].replace(",", ";") + ","
		if feature['id'] == "promotions":
			for value in feature['value']:
				 data['Акции'] += value['name'].replace(",", ";") + ","
	if data['Прочее'] != "":
		data['Прочее'] = data['Прочее'][:-1]
	if data['Виды работ'] != "":
		data['Виды работ'] = data['Виды работ'][:-1]
	if data['Автострахование'] != "":
		data['Автострахование'] = data['Автострахование'][:-1]
	if data['Способ оплаты'] != "":
		data['Способ оплаты'] = data['Способ оплаты'][:-1]
	if data['Продажа автомобилей'] != "":
		data['Продажа автомобилей'] = data['Продажа автомобилей'][:-1]
	if data['Акции'] != "":
		data['Акции'] = data['Акции'][:-1]
	parse_comments(data, salon['ratingData']['reviewCount'], salon_id)

with open("avto-ru-dealers.csv", encoding = 'utf-8') as f:
    print("Starting parser...")
    data = [dat.strip() for dat in f.readlines()]
    # Progress: 1.09% 58/5345 salons
    start = 59
    data = data[start:]
    work = True
    if start == 1:
	    keys = ['url', 'Сеть', 'Название салона', 'Название салона донора', 'Общий рейтинг салона', 
	    		'Телефон салона', 'Адрес салона', 'Официальный сайт', 'Прочее', 'Виды работ', 'Автострахование', 
	    		'Способ оплаты', 'Продажа автомобилей', 'Акции', 'Аватарка автора', 'Имя', 'Рейтинг', 
	    		'Текст отзыва', 'Дата отзыва', 'Лайки', 'Дизлайки', 'Фото отзыва', 'Официальный ответ']
	    with open(file_name, 'w') as f:
		    w = csv.DictWriter(f, keys)
		    w.writeheader()
    for id,line in enumerate(data):
        line = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line) 
        meta = {}
        meta['url'] = line[0]
        meta['Сеть'] = line[2]
        meta['Название салона'] = line[6]
        # print(meta['Сеть'].lower())
        if work == True:
        # if meta['Название салона'] == salon_name and work == True:
            print("Parsing salon:", meta['Название салона'])
            # work = False # test
            params = {
                "csrfToken": csrfToken,
                "sessionId": sessionId,
                "ajax": "1",
                "text": meta['Название салона'],
                "lang": "ru_RU",
                "yandex_gid": 6,
                "origin": "maps-form",
                "results": 25,
                "z": 16,
                "ll": "37.50383000000002,55.598824063457066",
                "spn": spn,
                "snippets": "masstransit/2.x,panoramas/1.x,businessrating/1.x,businessimages/1.x,photos/2.x,experimental/1.x,subtitle/1.x,visits_histogram/2.x,tycoon_owners_personal/1.x,tycoon_posts/1.x,related_adverts/1.x,related_adverts_1org/1.x,city_chains/1.x,route_point/1.x,topplaces/1.x,metrika_snippets/1.x,place_summary/1.x,online_snippets/1.x,building_info_experimental/1.x,provider_data/1.x,service_orgs_experimental/1.x,business_awards_experimental/1.x,business_filter/1.x,attractions/1.x,potential_company_owners:user,pin_info/1.x,fuel/1.x,realty_experimental/2.x,matchedobjects/1.x,discovery/1.x,topobjects/1.x,hot_water/1.x,showtimes/1.x,afisha_json_geozen/1.x,encyclopedia/1.x,stories_experimental/1.x,realty_buildings/1.x,bookings/1.x,bookings_personal/1.x",
                "add_type": "direct",
                "direct_page_id": 670942,
                "parent_reqid": parent_reqid,
                "experimental": [
                    "rearr=scheme_Local/Geo/Postfilter/Irrel=false",
                    "relev_ranking_heavy_relev_maps_formula=0.6:l3_fml780364",
                    "relev_ranking_heavy_relev_serp_formula=0.64:l3_fml_10993",
                    "relev_ranking_heavy_click_serp_formula=0.36:l3_fml751240"
                ],
                "test-buckets": test_buckets
            }
            x = {}
            for key in sorted(params):
                x[key] = params[key]
            params = x
            search = urllib.parse.urlencode(params, True)
            search = search.replace("+", "%20")
            search = search.replace("&experimental=rearr%3Dscheme_Local%2FGeo%2FPostfilter%2FIrrel%3Dfalse&experimental=relev_ranking_heavy_relev_maps_formula%3D0.6%3Al3_fml780364&experimental=relev_ranking_heavy_relev_serp_formula%3D0.64%3Al3_fml_10993&experimental=relev_ranking_heavy_click_serp_formula%3D0.36%3Al3_fml751240", "&experimental%5B0%5D=rearr%3Dscheme_Local%2FGeo%2FPostfilter%2FIrrel%3Dfalse&experimental%5B1%5D=relev_ranking_heavy_relev_maps_formula%3D0.6%3Al3_fml780364&experimental%5B2%5D=relev_ranking_heavy_relev_serp_formula%3D0.64%3Al3_fml_10993&experimental%5B3%5D=relev_ranking_heavy_click_serp_formula%3D0.36%3Al3_fml751240")
            s = generate_s(search)
            cookies = {
			    'yandexuid': yandexuid,
			    'Session_id': sessionIdCookie,
			}
            headers = {
            }
            params = (
                ('add_type', 'direct'),
                ('ajax', '1'),
                ('csrfToken', csrfToken),
                ('direct_page_id', '670942'),
                ('experimental[0]', 'rearr=scheme_Local/Geo/Postfilter/Irrel=false'),
                ('experimental[1]', 'relev_ranking_heavy_relev_maps_formula=0.6:l3_fml780364'),
                ('experimental[2]', 'relev_ranking_heavy_relev_serp_formula=0.64:l3_fml_10993'),
                ('experimental[3]', 'relev_ranking_heavy_click_serp_formula=0.36:l3_fml751240'),
                ('lang', 'ru_RU'),
                ('ll', '37.50383000000002,55.598824063457066'),
                ('origin', 'maps-form'),
                ('parent_reqid', parent_reqid),
                ('results', '25'),
                ('s', str(s)),
                ('sessionId', sessionId),
                ('snippets', 'masstransit/2.x,panoramas/1.x,businessrating/1.x,businessimages/1.x,photos/2.x,experimental/1.x,subtitle/1.x,visits_histogram/2.x,tycoon_owners_personal/1.x,tycoon_posts/1.x,related_adverts/1.x,related_adverts_1org/1.x,city_chains/1.x,route_point/1.x,topplaces/1.x,metrika_snippets/1.x,place_summary/1.x,online_snippets/1.x,building_info_experimental/1.x,provider_data/1.x,service_orgs_experimental/1.x,business_awards_experimental/1.x,business_filter/1.x,attractions/1.x,potential_company_owners:user,pin_info/1.x,fuel/1.x,realty_experimental/2.x,matchedobjects/1.x,discovery/1.x,topobjects/1.x,hot_water/1.x,showtimes/1.x,afisha_json_geozen/1.x,encyclopedia/1.x,stories_experimental/1.x,realty_buildings/1.x,bookings/1.x,bookings_personal/1.x'),
                ('spn', spn),
                ('test-buckets', test_buckets),
                ('text', meta['Название салона']),
                ('yandex_gid', '6'),
                ('z', '16'),
            )
            response = requests.get('https://yandex.ru/maps/api/search', headers=headers, params=params, cookies=cookies)
            # print(response.text)
            try:
            	parse_salon(meta, response)
            	print("Progress: " + str(round((id+1)/len(data)*100, 2)) + "% " + str(id+1) + "/" + str(len(data)) + " salons")
            except Exception:
            	print("error")
print("Completed!")












