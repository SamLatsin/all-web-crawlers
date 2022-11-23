import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import csv

file_name = "output.csv"
url = "https://spys.one/proxies/"

def checkCount(driver):
    while(driver.find_element(By.CSS_SELECTOR, "#xpp > option[selected]").text != "500"):
        driver.find_element(By.ID, "xpp").click()
        driver.find_elements(By.CSS_SELECTOR, "#xpp > option")[-1].click()

def checkAnonimity(driver):
    while(driver.find_element(By.CSS_SELECTOR, "#xf1 > option[selected]").text != "A+H"):
        driver.find_element(By.ID, "xf1").click()
        driver.find_elements(By.CSS_SELECTOR, "#xf1 > option")[1].click()

def checkType(driver):
    while(driver.find_element(By.CSS_SELECTOR, "#xf5 > option[selected]").text != "SOCKS"):
        driver.find_element(By.ID, "xf5").click()
        driver.find_elements(By.CSS_SELECTOR, "#xf5 > option")[2].click()

def main(driver):
    print("getting: " + url)
    driver.get(url)
    checkCount(driver)
    checkAnonimity(driver)
    checkType(driver)
    lines1 = driver.find_elements(By.CSS_SELECTOR, "tr.spy1xx > td:nth-child(1) > font:nth-child(1)")
    lines1 = lines1[1:] # skip header
    lines2 = driver.find_elements(By.CSS_SELECTOR, "tr.spy1x > td:nth-child(1) > font:nth-child(1)")
    lines2 = lines2[1:] # skip header
    lines = lines1 + lines2
    for index, line in enumerate(lines):
        line = line.text
        fields = {
            'ip': line.split(":")[0],
            'port': line.split(":")[1]
        }
        with open(file_name, 'a', encoding = 'utf-8') as f:
            w = csv.DictWriter(f, fields.keys())
            w.writerow(fields)
        print(line)

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
    options.headless = True # make headless work
    keys = ["ip", "port"]
    with open(file_name, 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
    driver = webdriver.Firefox(options = options, firefox_profile = profile)
    try:
        main(driver)
        print("Done")
        driver.close()
    except Exception:
        try:
            driver.close()
        except Exception:
            pass