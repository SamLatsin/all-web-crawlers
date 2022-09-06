import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import re
import math
import json
import csv
import pycountry

file_name = "forexbrokerz.csv"

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

def parse_type_a(driver, data):
    data['type'] = "A"
    try:
        table = driver.find_elements(By.CSS_SELECTOR, 'table[width]')[0]
        row = table.find_elements(By.CSS_SELECTOR, 'tr')[1]
        data['min_max_bet_size'] = row.find_elements(By.CSS_SELECTOR, 'td')[1].text
        data['payout'] = row.find_elements(By.CSS_SELECTOR, 'td')[2].text
        data['platform'] = row.find_elements(By.CSS_SELECTOR, 'td')[3].text
    except Exception:
        data['min_max_bet_size'] = ""  
        data['payout'] = ""  
        data['platform'] = ""  

    try:
        tradings_options = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p')
        for trading_options in tradings_options:
            if trading_options.text.find("Trading Options") != -1:
                temp = trading_options.text
                temp = temp.split(":")[1].strip()
                data['trading_options'] = temp
    except Exception:
        data['trading_options'] = ""

    try:
        assets = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p + p')
        for asset in assets:
            if asset.text.find("Assets:") != -1:
                temp = asset.text
                temp = temp.split(":")[1].strip()
                data['assets'] = temp
    except Exception:
        data['assets'] = ""

    try:
        h2s = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2')
        for index,h2 in enumerate(h2s):
            if h2.text.strip().lower() == "methods of payment":
                temp = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p')[index-2]
                data['methods_of_payment'] = temp.text
    except Exception:
        data['methods_of_payment'] = ""

    try:
        pros = []
        cons = []
        table = driver.find_elements(By.CSS_SELECTOR, 'table[width]')[-1]
        rows = table.find_elements(By.CSS_SELECTOR, 'tr')[1:]
        for row in rows:
            pros.append(row.find_elements(By.CSS_SELECTOR, 'td')[0].text.strip())
            cons.append(row.find_elements(By.CSS_SELECTOR, 'td')[1].text.strip())
        data['pros'] = ','.join(filter(None, pros))
        data['cons'] = ','.join(filter(None, cons))
    except Exception:
        data['pros'] = ""
        data['cons'] = ""
    return data

def parse_type_b(driver, data):
    data['type'] = "B"
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > div:not(.post-featured):not(.broker):not(.cf):not(.broker_review_rating_wrap)')
        data['minimum_trade_size'] = ""
        data['maximum_trade_size'] = ""
        data['bonus'] = ""
        data['payout'] = ""
        data['refund'] = ""
        data['option_types'] = ""
        data['types_of_assets'] = ""
        data['expiry_times'] = ""
        data['deposit_methods'] = ""
        data['withdrawal_methods'] = ""
        data['account_currencies'] = ""
        data['trading_platform'] = ""
        data['extra_services'] = ""
        data['website'] = ""
        data['headquaters'] = ""
        data['founded'] = ""
        data['regulated_by'] = ""
        data['languages'] = ""
        data['country'] = ""
        data['phone'] = ""
        is_phone = False
        for row in rows:
            if (is_phone):
                phones = row.text.split(",")
                stripped = [s.strip() for s in phones]
                data['phone'] = ','.join(filter(None, stripped))
                is_phone = False
            if (row.text.strip() == "Support Telephone Numbers:"):
                is_phone = True
            temp = row.text.split("\n")
            if len(temp) == 2:
                for rw in temp:
                    rw = rw.split(":")
                    if len(rw) == 2:
                        key = rw[0].lower().strip()
                        value = rw[1].strip()
                        if (key == "deposit methods"):
                            data['deposit_methods'] = value
                        if (key == "withdrawal methods"):
                            data['withdrawal_methods'] = value
            row = row.text.split(":")
            if len(row) == 2:
                key = row[0].lower().strip()
                value = row[1].strip()
                if (key == "minimum trade size"):
                    data['minimum_trade_size'] = value
                if (key == "maximum trade size"):
                    data['maximum_trade_size'] = value
                if (key == "bonus"):
                    data['bonus'] = value
                if (key == "payout"):
                    data['payout'] = value
                if (key == "refund"):
                    data['refund'] = value
                if (key == "option types"):
                    data['option_types'] = value
                if (key == "types of assets"):
                    data['types_of_assets'] = value
                if (key == "expiry times"):
                    data['expiry_times'] = value
                if (key == "account currencies"):
                    data['account_currencies'] = value
                if (key == "trading platform"):
                    data['trading_platform'] = value
                if (key == "extra services"):
                    data['extra_services'] = value
                if (key == "website"):
                    data['website'] = value
                if (key == "headquaters"):
                    data['headquaters'] = value
                if (key == "country"):
                    data['country'] = value
                if (key == "founded"):
                    data['founded'] = value
                if (key == "regulated by"):
                    data['regulated_by'] = value
                if (key == "languages"):
                    data['languages'] = value
    except Exception as e:
        print(e)
        pass
    return data

def parse_type_c(driver, data):
    data['type'] = "C"
    try:
        table = driver.find_elements(By.CSS_SELECTOR, 'table[width]')[0]
        row = table.find_elements(By.CSS_SELECTOR, 'tr')[1]
        data['min_max_bet_size'] = row.find_elements(By.CSS_SELECTOR, 'td')[1].text
        data['payout'] = row.find_elements(By.CSS_SELECTOR, 'td')[2].text
        data['platform'] = row.find_elements(By.CSS_SELECTOR, 'td')[3].text
    except Exception:
        data['min_max_bet_size'] = ""  
        data['payout'] = ""  
        data['platform'] = ""  

    tables = driver.find_elements(By.CSS_SELECTOR, 'table[width]')
    if len(tables) >= 3:
        try:
            t_data = []
            keys = []
            table = tables[1]
            rows = table.find_elements(By.CSS_SELECTOR, 'tr')
            for index,row in enumerate(rows):
                cols = row.find_elements(By.CSS_SELECTOR, 'td')
                if index == 0:
                    for col in cols:
                        keys.append(col.text.strip())
                else:
                    t_row = {}
                    for index1,col in enumerate(cols):
                        t_row[keys[index1]] = col.text.strip()
                    t_data.append(t_row)
            data['trading_accounts'] = json.dumps(t_data)
        except Exception as e:
            print(e)
            data['trading_accounts'] = ""
    
    all_text = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > p')
    stripped = [s.text.strip() for s in all_text]
    all_text = " ".join(stripped)
    found = False
    for country in pycountry.countries:
        if not found:
            if country.name in all_text:
                data['founded_in'] = country.name
                found = True

    try:
        tradings_options = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p')
        for trading_options in tradings_options:
            if trading_options.text.find("Trading Options") != -1:
                temp = trading_options.text
                temp = temp.split(":")[1].strip()
                data['trading_options'] = temp
    except Exception:
        data['trading_options'] = ""

    try:
        assets = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p + p')
        for asset in assets:
            if asset.text.find("Assets:") != -1:
                temp = asset.text
                temp = temp.split(":")[1].strip()
                data['assets'] = temp
    except Exception:
        data['assets'] = ""

    try:
        assets = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p + p + p')
        for asset in assets:
            if asset.text.find("Expiry times:") != -1:
                temp = asset.text
                temp = temp.split(":")[1].strip()
                data['expiry_times'] = temp
    except Exception:
        data['expiry_times'] = ""

    try:
        h2s = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2')
        for index,h2 in enumerate(h2s):
            if h2.text.strip().lower() == "methods of payment":
                temp = driver.find_elements(By.CSS_SELECTOR, '.post-content-bd > h2 + p')[index-2]
                data['methods_of_payment'] = temp.text
    except Exception:
        data['methods_of_payment'] = ""

    try:
        pros = []
        cons = []
        table = driver.find_elements(By.CSS_SELECTOR, 'table[width]')[-1]
        rows = table.find_elements(By.CSS_SELECTOR, 'tr')[1:]
        for row in rows:
            pros.append(row.find_elements(By.CSS_SELECTOR, 'td')[0].text.strip())
            cons.append(row.find_elements(By.CSS_SELECTOR, 'td')[1].text.strip())
        data['pros'] = ','.join(filter(None, pros))
        data['cons'] = ','.join(filter(None, cons))
    except Exception:
        data['pros'] = ""
        data['cons'] = ""

    return data

def parse_broker(driver, link, data):
    print("getting: " + link)
    driver.get(link)
    try:
        name = driver.find_elements(By.CSS_SELECTOR, 'h1')[0].text
        index = name.find("review")
        if index == -1:
            index = name.find("Review")
            if index == -1:
                data['name'] = ""
            else:
                data['name'] = name[0:index]
        else:
            data['name'] = name[0:index]
        data['name'] = data['name'].strip()
    except Exception:
        data['name'] = ""
    try:
        data['rating'] = driver.find_elements(By.CSS_SELECTOR, '.broker_review_rating_text')[0].text
        data['rating'] = re.findall("\d+\.\d+",data['rating'])[0]
    except Exception:
        data['rating'] = 0 
    try:
        tables = driver.find_elements(By.CSS_SELECTOR, 'table[width]')
        test_table = tables[1]
        rows = test_table.find_elements(By.CSS_SELECTOR, 'tr')
        if len(rows) > 2:
            # TYPE C
            print("TYPE C")
            data = parse_type_c(driver, data)
        else:
            # TYPE A
            print("TYPE A")
            data = parse_type_a(driver, data)
    except Exception:
        # TYPE B
        print("TYPE B")
        data = parse_type_b(driver, data)
    print(data)
    
    keys = ['cons', 'methods_of_payment', 'bonus', 'link', 'pros', 
            'option_types', 'regulated_by', 'name', 'min_deposit', 
            'founded_in', 'max_payout', 'website', 'regulation', 
            'platform', 'min_max_bet_size', 'headquaters', 'withdrawal_methods', 
            'types_of_assets', 'refund', 'rating', 'payout', 'minimum_trade_size', 
            'account_currencies', 'assets', 'expiry_times', 'img_link', 
            'extra_services', 'deposit_methods', 'trading_options', 'trading_platform', 
            'phone', 'languages', 'country', 'maximum_trade_size', 'type', 
            'founded', 'trading_accounts']
    output_data = {}
    for key in keys:
        output_data[key] = None

    for key in data:
        output_data[key] = data[key]


    with open(file_name, 'a', encoding = 'utf-8') as f:
        w = csv.DictWriter(f, output_data.keys())
        w.writerow(output_data)
    
def parse_listing_page(driver, page=1):
    # test = {'img_link': 'data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%20210%20140%22%3E%3C/svg%3E', 'country': 'SVG', 'regulation': 'N/A', 'min_deposit': '$10', 'max_payout': '86%', 'link': 'https://www.forexbrokerz.com/brokers/binary-online', 'name': 'Grand Capital Option', 'rating': '1.9'}
    # parse_broker(driver, test['link'], test)
    link = "https://www.forexbrokerz.com/binary-brokers.php?page=" + str(page)
    print("getting: " + link)
    driver.get(link)
    try:
        next_page = driver.find_elements(By.CSS_SELECTOR, '.pagenavi-next')[0].get_attribute('href')
        next_page = get_numbers(next_page)[0]
    except Exception:
        next_page = False
    brokers = driver.find_elements(By.CSS_SELECTOR, '.brokers_list_tbl tr[data-tr-label]')
    brokers_data = []
    for broker in brokers:
        data = {}
        try:
            data['img_link'] = broker.find_elements(By.CSS_SELECTOR, '.brlogo')[0].get_attribute('src')
            data['country'] = broker.find_elements(By.CSS_SELECTOR, 'td:nth-child(2)')[0].text
            data['country'] = data['country'].replace("\nHighLow Review", "")
            data['regulation'] = broker.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')[0].text
            data['min_deposit'] = broker.find_elements(By.CSS_SELECTOR, 'td:nth-child(4)')[0].text
            data['min_deposit'] = broker.find_elements(By.CSS_SELECTOR, 'td:nth-child(4)')[0].text
            data['max_payout'] = broker.find_elements(By.CSS_SELECTOR, 'td:nth-child(5)')[0].text
            try:
                data['link'] = broker.find_elements(By.CSS_SELECTOR, 'a:not(.bd_button)')[0].get_attribute('href')
                brokers_data.append(data)
            except Exception:
                pass
        except Exception:
            pass
    for broker_data in brokers_data:
        parse_broker(driver, broker_data['link'], broker_data)
    if next_page != False:
        parse_listing_page(driver, next_page)

def main(driver):
    link = "https://www.forexbrokerz.com/binary-brokers.php"
    parse_listing_page(driver)

if __name__ == "__main__":
    options = Options()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.http.pipelining", True)
    profile.set_preference("network.http.proxy.pipelining", True)
    profile.set_preference("network.http.pipelining.maxrequests", 8)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
    profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
    profile.set_preference("loop.enabled", False)
    profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
    profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
    profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
    profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
    profile.set_preference("browser.display.use_system_colors", True) # Use system colors.
    profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0) # blank
    profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
    profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
    profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
    profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
    profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
    profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("permissions.default.image", 2) # Image load disabled again
    profile.set_preference("permissions.default.stylesheet", 2);

    # options.headless = True

    keys = ['cons', 'methods_of_payment', 'bonus', 'link', 'pros', 
            'option_types', 'regulated_by', 'name', 'min_deposit', 
            'founded_in', 'max_payout', 'website', 'regulation', 
            'platform', 'min_max_bet_size', 'headquaters', 'withdrawal_methods', 
            'types_of_assets', 'refund', 'rating', 'payout', 'minimum_trade_size', 
            'account_currencies', 'assets', 'expiry_times', 'img_link', 
            'extra_services', 'deposit_methods', 'trading_options', 'trading_platform', 
            'phone', 'languages', 'country', 'maximum_trade_size', 'type', 
            'founded', 'trading_accounts']

    with open(file_name, 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()

    # make headless work
    driver = webdriver.Firefox(options = options, firefox_profile = profile)
    main(driver)






        
















