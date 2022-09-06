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

file_name = "forexbrokerz_imgs.csv"

def remove_spaces(text):
    return re.sub(' +', ' ', text.strip())
def get_numbers(text):
    return re.findall(r'\d+', text)

def parse_page(link, driver):
    print("getting: " + link)
    driver.get(link)
    output_data = {}
    output_data['link'] = driver.current_url
    try:
        output_data['img'] = driver.find_elements(By.CSS_SELECTOR, '.attachment-bd-big')[0].get_attribute('src')
    except Exception:
        try:
            output_data['img'] = driver.find_elements(By.CSS_SELECTOR, '.rating_section_logo > img:nth-child(2)')[0].get_attribute('src')
        except Exception:
            output_data['img'] = ""
    
    with open(file_name, 'a', encoding = 'utf-8') as f:
        w = csv.DictWriter(f, output_data.keys())
        w.writerow(output_data)
    print(output_data['img'])

def main(driver):
    with open("forexbrokers_links.txt", 'r') as f:
        links = f.readlines()
        links = [link.rstrip() for link in links]
    for link in links:
        parse_page(link, driver)
       

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

    keys = ['link', 'img']

    with open(file_name, 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()

    # make headless work
    driver = webdriver.Firefox(options = options, firefox_profile = profile)
    main(driver)






        
















