import json
import math
import os

import requests

cookies = {
    'spravka': 'dD0xNjQ5ODUzNTg0O2k9MTc2LjU5LjE2MC4xO0Q9RDQzMzZDOTE1RDlDQzg3QkY2QzhBQ0RGMDkzMjI2NTBDRkQzNDZDMzM5QkEzMDA1MzI4NEI0RjVDOTE0NjJCRjA0MTlEMkU4O3U9MTY0OTg1MzU4NDMzMjY0NDI5ODtoPWZlYmZkYTIxNjM3ODJiZDY1NWU5YTZkMjVjYzVkMTQ3',
    '_csrf_token': 'cea4466918d3c1dd79b5a5e82162e8e23984c05253ec172c',
    'yandex_login': '',
    'suid': 'aa7561301af62e30b76ef155da798712.67d2b523ec5fcff97f2fda9899fca62f',
    'from_lifetime': '1649952844555',
    'from': 'direct',
    '_yasc': 'hfHuI6KbiRhqvcHwdMLRZr+p/uh0m/UNz7Sjo27JjrU5AKdL',
    'yuidlt': '1',
    'yandexuid': '3681872781632383078',
    'my': 'YwA%3D',
    'autoru_sid': 'a%3Ag6256cb952efp20v209o9ohl8r9q1fuc.706c99ebe98bb3f8ad5e5f925b55fdce%7C1649855381839.604800.7qhYcTgjkUx_azXOnj_0jQ.RlMsDImtVetwJSsSL4u2krgZbnfBDgcpFwauIWje0BI',
    'autoruuid': 'g6256cb952efp20v209o9ohl8r9q1fuc.706c99ebe98bb3f8ad5e5f925b55fdce',
    'autoru-visits-count': '4',
    'ys': 'c_chck.3034321856',
    'i': 'XsnsYsvDARurYrZdiBU9s4NPsAnNxG62sfOpNP1QNDoWWi/3kT0+fq30dcque3YotMBskiuaaIVeruRB93S94YeQMMY=',
    'mda2_beacon': '1649947629413',
    'los': '1',
    'bltsr': '1',
    'credit_filter_promo_popup_closed': 'true',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

def processPage(text):
    start = '"price_info":{"price":'
    end = ',"with_nds":'
    res = {}
    final_json = text[text.find(start):text.find(end)] + '}'
    final_json = final_json[final_json.find('{'):]
    if final_json != "}": # update price
        obj = json.loads(final_json)
        try:
            res['price'] = obj['price']
        except Exception:
            pass
        try: 
            res['priceUSD'] = obj['USD']
        except Exception:
            pass
        try:
            res['priceEUR'] = obj['EUR']
        except Exception:
            pass
        return res

    sold = 'class="CardSold"'
    if text.find(sold) != -1: # set sold status
        res['sold'] = 1
        return res

    return res

def getCarsCount():
    token = "xLmxLZ7Sk3vqPBrsWUyb5hrZDqmLzRkz"

    data = {
        'token': token,
    }
    response = requests.post('http://your-site/parsing/get_cars_count', data=data)
    return response.text

def getCars(page, limit):
    token = "xLmxLZ7Sk3vqPBrsWUyb5hrZDqmLzRkz"

    data = {
        'token': token,
        'page': page,
        'chunk_size': limit
    }
    response = requests.post('http://your-site/parsing/get_cars', data=data)
    return response.text

def updateDB(pool):
    token = "xLmxLZ7Sk3vqPBrsWUyb5hrZDqmLzRkz"

    data = {
        'token': token,
        'pool': json.dumps(pool)
    }
    response = requests.post('http://your-site/parsing/update_cars', data=data)
    return response

if __name__ == "__main__":
    with open(r"update_status_car_id.txt", encoding = 'utf-8') as f:
        start = int(f.readlines()[0])

    count = float(getCarsCount())
    limit = 100
    pages = math.ceil(count / limit)
    start_page = math.floor(start/limit)

    try:
        for page in range(0,pages):
            pool = []
            if page >= start_page:
                cars = getCars(page, limit)
                cars = json.loads(cars)
                for car in cars:
                    response = requests.get(car['linkOrig'], headers=headers, cookies=cookies) 
                    fields = processPage(response.text)
                    if fields:
                        print([car['id'], fields])
                        pool.append([car['id'], fields])
                    with open(r"update_status_car_id.txt", 'w') as f:
                        f.write(str(car['id']))
                updateDB(pool)

        with open(r"update_status_car_id.txt", 'w') as f:
            f.write("0")
    except Exception:
        os.system("python3 auto-ru-update.py")











