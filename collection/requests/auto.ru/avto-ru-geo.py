
import csv
import requests
import json
from time import sleep

token = '636224dafc34b7e0c38f88d0e90b7d6de0789c68d439dfb3'
coords = [38, 76, 18, 165] # Russia coords

f = csv.writer(open("avto-ru-dealers-geo.csv", "w", newline=''))

f.writerow(["url", "logo", "Сеть", "Адрес", "Метро", "Авто в наличие"])

cookies = {
    '_csrf_token': token,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0',
    'x-csrf-token': token,
    'content-type': 'application/json',
    'Origin': 'https://auto.ru',
}

def parse_by_coords(coords):
    data = {
        "category": "cars",
        "has-offers": False,
        "place_lat_from": coords[0],
        "place_lat_to": coords[1],
        "place_lon_from": coords[2],
        "place_lon_to": coords[3],
        "section": "all"
    }
    data = json.dumps(data)
    response = requests.post('https://auto.ru/-/ajax/desktop/dealersListing/', headers=headers, cookies=cookies, data=data)

    dealers = json.loads(response.text)
    if (dealers['totalResultsCount'] > 300):
        print("more than 300 results (" + str(dealers['totalResultsCount']) + "), dividing...")
        coords1 = [coords[0], (coords[1]-coords[0])/2 + coords[0], coords[2], (coords[3]-coords[2])/2 + coords[2]]
        coords2 = [(coords[1]-coords[0])/2 + coords[0], coords[1], coords[2], (coords[3]-coords[2])/2 + coords[2]]
        coords3 = [coords[0], (coords[1]-coords[0])/2 + coords[0], (coords[3]-coords[2])/2 + coords[2], coords[3]]
        coords4 = [(coords[1]-coords[0])/2 + coords[0], coords[1], (coords[3]-coords[2])/2 + coords[2], coords[3]]
        parse_by_coords(coords1)
        parse_by_coords(coords2)
        parse_by_coords(coords3)
        parse_by_coords(coords4)
    else:
        print(str(dealers['totalResultsCount']) + " results, storing links...")
        data = {}
        for dealer in dealers['dealers']:
            data['url'] = "https://auto.ru/diler/cars/all/" + dealer["dealerCode"]
            try:
                data['logo'] = "https:" + dealer["dealerLogo"]
            except Exception:
                data['logo'] = ""
            try:
                data['Сеть'] = dealer["netName"]
            except Exception:
                data['Сеть'] = ""
            try:
                data['Адрес'] = dealer["address"]
            except Exception:
                data['Адрес'] = ""
            try:
                data['Метро'] = ""
                for metro in dealer['metro']:
                    data['Метро'] += metro['name'] + ","
                data['Метро'] = data['Метро'][:-1]
            except Exception:
                data['Метро'] = ""
            try:
                data['Авто в наличие'] = dealer["filteredOffersCount"]
            except Exception:
                data['Авто в наличие'] = ""
            f.writerow([data['url'],
                        data['logo'],
                        data['Сеть'],
                        data['Адрес'],
                        data['Метро'],
                        data['Авто в наличие']])

parse_by_coords(coords)







