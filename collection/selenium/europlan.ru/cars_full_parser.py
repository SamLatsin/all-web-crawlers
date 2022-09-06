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
	benefit = ""
	benefitLoan = ""
	priceWithDicount = ""
	term = ""
	every = ""
	imgBig = ""
	priceWithoutDiscount = ""

class Car(object):
	name = ""
	sub = ""
	slug = ""
	imageMin = ""
	cost = ""
	engine = ""
	power = ""
	typeEngine = ""
	box = ""
	body = ""
	unit = ""
	color = ""
	city = ""
	type = ""
	mark = ""
	model = ""
	every = ""

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

def update_db(model, db, id):
	print("Updating DB")
	cursor = db.cursor(buffered=True)
	if (model.benefit == ""):
		update_query = "UPDATE main.models SET benefitLoan = '{}', priceWithoutDiscount = '{}', term = '{}', every = '{}', imgBig = '{}'  WHERE id = '{}';".format(str(model.benefitLoan), str(model.priceWithoutDiscount), str(model.term), str(model.every), str(model.imgBig), str(id))
	else:
		update_query = "UPDATE main.models SET benefit = '{}', benefitLoan = '{}', priceWithDiscount = '{}', priceWithoutDiscount = '{}', term = '{}', every = '{}', imgBig = '{}'  WHERE id = '{}';".format(str(model.benefit), str(model.benefitLoan), str(model.priceWithDicount), str(model.priceWithoutDiscount), str(model.term), str(model.every), str(model.imgBig), str(id))
	try:
		cursor.execute(update_query)
		db.commit()
	except Exception as e:
		print(e)
		print("benefit: " + str(model.benefit) +
		 " benefitLoan: " + str(model.benefitLoan) +
		 " priceWithDicount: " + str(model.priceWithDicount) +
		 " priceWithoutDiscount: " + str(model.priceWithoutDiscount) +
		 " term: " + str(model.term) +
		 " every: " + str(model.every) +
		 " imgBig: " + str(model.imgBig))
	cursor.close()

def insert_to_db(cars, db):
	cursor = db.cursor(buffered=True)
	for car in cars:
		if car.type == 1:
			add_query = "INSERT INTO main.cars_full (name, sub, slug, imageMin, cost, engine, power, typeEngine, box, body, unit, color, city, type, mark, model, every) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(str(car.name), str(car.sub), str(car.slug), str(car.imageMin), str(car.cost), str(car.engine), str(car.power), str(car.typeEngine), str(car.box), str(car.body) , str(car.unit) , str(car.color) , str(car.city) , str(car.type) , str(car.mark) , str(car.model) , str(car.every))
		elif car.type == 2 or car.type == 5:
			add_query = "INSERT INTO main.cars_full (name, sub, slug, imageMin, cost, engine, power, typeEngine, box, unit, color, city, type, mark, model, every) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(str(car.name), str(car.sub), str(car.slug), str(car.imageMin), str(car.cost), str(car.engine), str(car.power), str(car.typeEngine), str(car.box), str(car.unit) , str(car.color) , str(car.city) , str(car.type) , str(car.mark) , str(car.model) , str(car.every))
		elif car.type == 8:
			add_query = "INSERT INTO main.cars_full (name, slug, imageMin, cost, color, city, type, mark, model, every) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(str(car.name), str(car.slug), str(car.imageMin), str(car.cost), str(car.color) , str(car.city) , str(car.type) , str(car.mark) , str(car.model) , str(car.every))
		try:
			cursor.execute(add_query)
			emp_no = cursor.lastrowid
			db.commit()
		except Exception as e:
			print(e)
			print("name: " + str(car.name) +
			 " sub: " + str(car.sub) +
			 " slug: " + str(car.slug) +
			 " imageMin: " + str(car.imageMin) +
			 " cost: " + str(car.cost) +
			 " engine: " + str(car.engine) +
			 " power: " + str(car.power) +
			 " typeEngine: " + str(car.typeEngine) +
			 " box: " + str(car.box) +
			 " body: " + str(car.body) +
			 " unit: " + str(car.unit) +
			 " color: " + str(car.color) +
			 " city: " + str(car.city) +
			 " type: " + str(car.type) +
			 " mark: " + str(car.mark) +
			 " model: " + str(car.model) +
			 " every: " + str(car.every))
	cursor.close()

def parse_cars_full(driver, array, db):
	dir = "C:\\Users\\User\\Desktop\\europlan parser\\"
	model = Model()	
	print("Going to link: " + array[1])
	driver.get(array[1])
	# обновление таблицы models
	print("Parsing benefit, benefitLoan, priceWithDicount, priceWithoutDiscount, term, every")
	try:
		if (len(driver.find_elements_by_class_name("conditions-item-strong")) == 4 ):
			model.benefit = ""
			model.benefitLoan = driver.find_elements_by_class_name("conditions-item-strong")[3].text
			model.priceWithDicount = ""
			model.priceWithoutDiscount = driver.find_elements_by_class_name("conditions-item-strong")[0].text
			model.term = driver.find_elements_by_class_name("conditions-item-strong")[1].text
			model.every = driver.find_elements_by_class_name("conditions-item-strong")[2].text
			imgs = driver.find_elements_by_css_selector("div.rel > pic:nth-child(1) > picture:nth-child(1) > img:nth-child(2)")
			model.imgBig = ""
			model.benefitLoan = "".join(re.findall('(\d+)', model.benefitLoan.replace(" ","")))
			model.term = "".join(re.findall('(\d+)', model.term.replace(" ","")))
			model.every = "".join(re.findall('(\d+)', model.every.replace(" ","")))
			model.priceWithoutDiscount = "".join(re.findall('(\d+)', model.priceWithoutDiscount.replace(" ","")))
		else:
			model.benefit = driver.find_elements_by_class_name("conditions-item-strong")[4].text
			model.benefitLoan = driver.find_elements_by_class_name("conditions-item-strong")[5].text
			model.priceWithDicount = driver.find_elements_by_class_name("conditions-item-strong")[0].text
			model.priceWithoutDiscount = driver.find_elements_by_class_name("conditions-item-strong")[1].text
			model.term = driver.find_elements_by_class_name("conditions-item-strong")[2].text
			model.every = driver.find_elements_by_class_name("conditions-item-strong")[3].text
			imgs = driver.find_elements_by_css_selector("div.rel > pic:nth-child(1) > picture:nth-child(1) > img:nth-child(2)")
			model.imgBig = ""
			model.benefit = "".join(re.findall('(\d+)', model.benefit.replace(" ","")))
			model.benefitLoan = "".join(re.findall('(\d+)', model.benefitLoan.replace(" ","")))
			model.priceWithDicount = "".join(re.findall('(\d+)', model.priceWithDicount.replace(" ","")))
			model.term = "".join(re.findall('(\d+)', model.term.replace(" ","")))
			model.every = "".join(re.findall('(\d+)', model.every.replace(" ","")))
			model.priceWithoutDiscount = "".join(re.findall('(\d+)', model.priceWithoutDiscount.replace(" ","")))
		print("Parsing imgBig")
		for img in imgs:
			if array[3] == 1:
				subfolder_to_img = "cars/"
				subfolder = "cars\\"
			elif array[3] == 2:
				subfolder_to_img = "trucks/"
				subfolder = "trucks\\"
			elif array[3] == 5:
				subfolder_to_img = "specs/"
				subfolder = "specs\\"
			elif array[3] == 8:
				subfolder_to_img = "prits/"
				subfolder = "prits\\"
			if (isAttribtuePresent(img, "src") and img.get_attribute("src") != ""):
				try:
					urllib.request.urlretrieve(img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
					model.imgBig = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
				except:
					urllib.request.urlretrieve("https://europlan.ru" + img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
					model.imgBig = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
		update_db(model, db, array[0])
	except Exception as e:
		print("Error " + str(e))
		print("Skipping")
	# наполнение таблицы full_cars
	if array[2] > 0:
		print("Parsing equipments")
		cars = []
		type = array[3]
		mark = driver.find_elements_by_class_name("ng-star-inserted")[3].text
		model = driver.find_elements_by_class_name("ng-star-inserted")[4].text
		for i in range(0, math.ceil(array[2]/10)):
			print("Parsing page " + str(i+1))
			driver.get(array[1] + "?page=" + str(i + 1))
			html = driver.find_element_by_tag_name('html')
			for i in range(0,10):
				html.send_keys(Keys.PAGE_DOWN)
				sleep(0.01)
			names = driver.find_elements_by_class_name("available-card__text-head")
			subs = driver.find_elements_by_class_name("available-card__text-text")
			slug = ""
			imageMins = driver.find_elements_by_css_selector("div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > pic:nth-child(2) > picture:nth-child(1) > img:nth-child(2)")
			costs = driver.find_elements_by_class_name("available-card__cont")
			print("Parsing names, slugs, types, marks, models")
			j = 0
			for name in names:
				cars.append(Car())
				cars[j].name = name.text
				cars[j].slug = transliterate.translit(name.text, 'uk', reversed=True)
				cars[j].type = type
				cars[j].mark = mark
				cars[j].model = model
				# print(str(j) + " " + str(cars[j].name) + " " + str(cars[j].type) + " " + str(cars[j].mark) + " " + str(cars[j].model) + str(cars[j].slug))
				j += 1
			j = 0
			print("Parsing subs, engines, powers, boxes, units, typeEngines, bodies, colors, cities")
			pos = 0
			for sub in subs:
				if (pos % 2 == 0):
					if (cars[j].type != 8):
						cars[j].sub = sub.text
						cars[j].engine = re.findall('(\d+)', sub.text.replace(" ",""))[0] + "," + re.findall('(\d+)', sub.text.replace(" ",""))[1]
						cars[j].power = re.findall('(\d+)', sub.text.replace(" ",""))[2]
						cars[j].box = re.findall('(\w+)', sub.text)[6]
						cars[j].unit = re.findall('(\w+)', sub.text)[7]
						cars[j].typeEngine = re.findall('(\w+)', sub.text)[2]
					if (cars[j].type == 1):
						cars[j].body = re.findall('(\w+)', sub.text)[8]
				if ((pos - 1) % 2 == 0):
					color = sub.text.split("\n")[1]
					city = sub.text.split("\n")[2]
					color = color[0:color.find(" ")]
					city = city[0:city.find("№")]
					cars[j].color = color
					cars[j].city = city
					# print(str(j) + " " + str(cars[j].sub) + " " + str(cars[j].engine) + " " + str(cars[j].power) + " " + str(cars[j].box) + " " + str(cars[j].unit) + " " + str(cars[j].typeEngine) + " " + str(cars[j].body) + " " + str(cars[j].color) + " " + str(cars[j].city))
					j += 1
				pos += 1
			j = 0
			print("Parsing costs, everies")
			pos = 0
			for cost in costs:
				if ((pos - 1) % 4 == 0):
					cars[j].cost = "".join(re.findall('(\d+)', cost.text.replace(" ","")))
				if ((pos - 3) % 4 == 0):
					cars[j].every = "".join(re.findall('(\d+)', cost.text.replace(" ","")))
					# print(str(j) + " " + str(cars[j].cost) + " " + str(cars[j].every))
					j += 1
				pos += 1
			j = 0
			print("Parsing imageMin")
			pos = 0
			for img in imageMins:
				if array[3] == 1:
					subfolder_to_img = "cars/"
					subfolder = "cars\\"
				elif array[3] == 2:
					subfolder_to_img = "trucks/"
					subfolder = "trucks\\"
				elif array[3] == 5:
					subfolder_to_img = "specs/"
					subfolder = "specs\\"
				elif array[3] == 8:
					subfolder_to_img = "prits/"
					subfolder = "prits\\"
				if (isAttribtuePresent(img, "src") and img.get_attribute("src") != ""):
					try:
						urllib.request.urlretrieve(img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
						cars[j].imageMin = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
						# print(str(j) + " " + str(cars[j].imageMin))
						j += 1
					except:
						try:
							urllib.request.urlretrieve("https://europlan.ru" + img.get_attribute("src"), dir + subfolder + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg")
							cars[j].imageMin = "http://panel.carfinance.ru/files/" + subfolder_to_img + re.findall('(\d+)', img.get_attribute("src"))[0] + ".jpg"
							# print(str(j) + " " + str(cars[j].imageMin))
							j += 1
						except Exception as e:
							print("Error " + str(e))
							print("Skipping")
				pos += 1

			print("Inserting into DB")
			insert_to_db(cars, db)
			cars = []

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
		# array = (58, "https://europlan.ru/auto/cars/chevrolet/spark", 0, 1)
		# parse_cars_full(driver, array, db)
		cursor_link = db.cursor(buffered=True)
		cursor_link.execute("SELECT id,link,count,type FROM main.models;")
		for array in cursor_link:
			parse_cars_full(driver, array, db)
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