# -*- coding: utf-8 -*-
import re
import os
import sys
import math
import urllib.request
import transliterate
import mysql.connector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


class Model(object):
	img = ""
	name = ""
	mark = ""
	slug = ""
	priceFrom = ""
	priceTo = ""
	type = ""
	minPrice = ""
	count = ""
	link = ""

delay = 10 # время поиска элемента на страницы в секундах

# функция проверки существования элемента по его id
def check_exists_by_id(element_id, max_delay, driver):
	driver.implicitly_wait(max_delay)
	try:
		driver.find_element_by_id(element_id)
	except NoSuchElementException:
		driver.implicitly_wait(delay)
		return False
	driver.implicitly_wait(delay)
	return True

# функция проверки существования элемента по его имени
def check_exists_by_name(element_name, max_delay, driver):
	driver.implicitly_wait(max_delay)
	try:
		driver.find_element_by_name(element_name)
	except NoSuchElementException:
		driver.implicitly_wait(delay)
		return False
	driver.implicitly_wait(delay)
	return True

# функция проверки существования элемента по его имени класса
def check_exists_by_class_name(class_name, max_delay, driver):
	driver.implicitly_wait(max_delay)
	try:
		driver.find_element_by_class_name(class_name)
	except NoSuchElementException:
		driver.implicitly_wait(delay)
		return False
	driver.implicitly_wait(delay)
	return True

# функция получения текста элемента по его id
def get_text_if_element_exists_by_id(element_id, driver, ldelay=2):
	if check_exists_by_id(element_id, ldelay, driver):
		return driver.find_element_by_id(element_id).text
	else:
		return ""

# функция поиска конкретного элемента по подстроке и имени класса
def find_element_by_text_in_elements_class_name(text, class_name, driver):
	elements = driver.find_elements_by_class_name(class_name)
	for element in elements:
		if element.text.lower().find(text) != -1 and element.text.lower().find(text) < 5:
			return element

def isAttribtuePresent(element, attribute):
	result = False
	try:
		value = element.get_attribute(attribute)
		if (value != None):
			result = True
	except Exception as e:
			print("Error " + str(e))
	return result

def push_objects_in_db(models, db):
	print("Inserting into DB")
	cursor = db.cursor(buffered=True)
	for model in models:
		if (model.priceTo == ""):
			add_query = "INSERT INTO main.models (img, name, mark, slug, priceFrom, type, minPrice, count, link) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(str(model.img), str(model.name), str(model.mark), str(model.slug), str(model.priceFrom), str(model.type), str(model.minPrice), str(model.count), str(model.link))
		else:
			add_query = "INSERT INTO main.models (img, name, mark, slug, priceFrom, priceTo, type, minPrice, count, link) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(str(model.img), str(model.name), str(model.mark), str(model.slug), str(model.priceFrom), str(model.priceTo), str(model.type), str(model.minPrice), str(model.count), str(model.link))
		try:
			cursor.execute(add_query)
			emp_no = cursor.lastrowid
			db.commit()
		except Exception as e:
			print(e)
			print("img: " + str(model.img) +
			 " name: " + str(model.name) +
			 " mark: " + str(model.mark) +
			 " slug: " + str(model.slug) +
			 " priceFrom: " + str(model.priceFrom) +
			 " priceTo: " + str(model.priceTo) +
			 " type: " + str(model.type) +
			 " minPrice: " + str(model.minPrice) +
			 " count: " + str(model.count) +
			 " link: " + str(model.link))
	cursor.close()
		# print("img: " + str(model.img) +
		# 	 " name: " + str(model.name) +
		# 	 " mark: " + str(model.mark) +
		# 	 " slug: " + str(model.slug) +
		# 	 " priceFrom: " + str(model.priceFrom) +
		# 	 " priceTo: " + str(model.priceTo) +
		# 	 " type: " + str(model.type) +
		# 	 " minPrice: " + str(model.minPrice) +
		# 	 " count: " + str(model.count) +
		# 	 " link: " + str(model.link))

def parse_models(driver, crop_link, db):
	dir = "C:\\Users\\User\\Desktop\\europlan parser\\"
	models = []
	print("Going to link: https://europlan.ru" + crop_link)
	driver.get("https://europlan.ru" + crop_link) # переход на сайт
	names = driver.find_elements_by_class_name("am-card__cont-head")
	mark = driver.find_elements_by_class_name("ng-star-inserted")[3].text
	slugs = []
	pricesRange = driver.find_elements_by_class_name("am-card__cont-price")
	pricesTo = ""
	types = ""
	minPrices = driver.find_elements_by_class_name("am-card__cont-paylink")
	counts = driver.find_elements_by_class_name("am-card__cont-avlink")
	links = driver.find_elements_by_class_name("am-card__cont-head")

	if crop_link.find("cars") != -1:
		type = 1
	elif crop_link.find("commercial") != -1:
		type = 2
	elif crop_link.find("special") != -1:
		type = 5
	elif crop_link.find("trailer") != -1:
		type = 8

	html = driver.find_element_by_tag_name('html')
	for i in range(0,10):
		html.send_keys(Keys.PAGE_DOWN)
		sleep(0.1)
	i = 0
	print("Parsing names, mark, type, slug")
	for name in names:
		models.append(Model())
		models[i].name = name.text
		models[i].mark = mark
		models[i].type = type
		models[i].slug = transliterate.translit(name.text, 'uk', reversed=True)
		i += 1
	i = 0
	print("Parsing pricesFrom and pricesTo")
	for priceRange in pricesRange:
		priceFrom = priceRange.text.replace(" ", "")[0:priceRange.text.replace(" ", "").find("₽")]
		priceTo = priceRange.text.replace(" ", "")[priceRange.text.replace(" ", "").find("–") + 1:priceRange.text.replace(" ", "").rfind("₽")]
		if priceTo == priceFrom:
			priceTo = ""
		models[i].priceFrom = priceFrom
		models[i].priceTo = priceTo
		i += 1
	i = 0
	print("Parsing minPrices")
	for minPrice in minPrices:
		models[i].minPrice = "".join(re.findall('(\d+)', minPrice.text))
		i += 1
	i = 0
	print("Parsing counts")
	for count in counts:
		if "".join(re.findall('(\d+)', count.text)) != "":
			models[i].count = "".join(re.findall('(\d+)', count.text))
			i += 1
		else:
			models[i].count = 0
			i += 1
	i = 0
	print("Parsing links")
	for link in links:
		models[i].link = link.get_attribute("href")
		i += 1
	i = 0
	print("Parsing imgs")
	imgs = driver.find_elements_by_class_name("ng-star-inserted")
	for img in imgs:
		if type == 1:
			subfolder_to_img = "cars/"
			subfolder = "cars\\"
		elif type == 2:
			subfolder_to_img = "trucks/"
			subfolder = "trucks\\"
		elif type == 5:
			subfolder_to_img = "specs/"
			subfolder = "specs\\"
		elif type == 8:
			subfolder_to_img = "prits/"
			subfolder = "prits\\"

		if (isAttribtuePresent(img, "src") and img.get_attribute("src") != ""):
			try:
				urllib.request.urlretrieve(img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
				models[i].img = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
				i += 1
			except:
				urllib.request.urlretrieve("https://europlan.ru" + img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
				models[i].img = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
				i += 1
	push_objects_in_db(models, db)

def main():
	try:
		# установка настроек браузера
		options = Options()
		# options.headless = args.headless # режим без открытия браузера(скрытый режим)
		driver = webdriver.Firefox(options=options)
		driver.implicitly_wait(delay)
		# начало работы

		db = mysql.connector.connect(user='', password='',
                              host='127.0.0.1',
                              database='main')
		cursor_link = db.cursor(buffered=True)
		cursor_link.execute("SELECT link FROM main.model_links;")
		for link in cursor_link:
			if link[0] != None:
				parse_models(driver, link[0], db)
		# crop_link = "/auto/cars/bmw"
		print("Done")
		cursor_link.close()
		db.close()
		driver.quit()
	except KeyboardInterrupt:
		driver.quit()
		cursor_link.close()
		db.close()

if __name__ == "__main__":
	main()
