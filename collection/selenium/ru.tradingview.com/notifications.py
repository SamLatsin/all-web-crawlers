# -*- coding: utf-8 -*-
import sys
import math
import argparse
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

username = "" # логин
password = "" # пароль
interval = "1 час" # интервал времени
condition_dict = {'trend': 1, "fli": 2, "tux": 3} # словарик с существующими условиями
delay = 10 # время поиска элемента на страницы в секундах

# парсинг аргументов запуска
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-s", "--signals", action = "store_true",
                    help='add all signals (trend, fli, tux)')
group.add_argument("-c", "--condition", type=str,
                    help='specify signal (eg: fli or trend or tux)')
group.add_argument("-r", "--remove", action = "store_true",
                    help='remove all signals')
group.add_argument("--stop", action = "store_true",
                    help='stop signal')
group.add_argument("--start", action = "store_true",
                    help='start signal')
parser.add_argument("-t", "--ticker", required=True, type=str,
                    help='specify ticker')
parser.add_argument("--headless", action = "store_true",
                    help='use headless mode(no browser)')
args = parser.parse_args()

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

# функция установки webhook
def webhook(driver):
	url_element = driver.find_element_by_class_name("tv-control-input--size_small")
	url_element.clear()
	if condition == "trend":
		url = "https://trendbot.ru/api/add/signal/" + ticker.lower() + "/" + str(condition) + "/" + "long"
		url_element.send_keys(url)
	else:
		url = "https://trendbot.ru/api/add/signal/" + ticker.lower() + "/" + str(condition) + "/" + "buy"
		url_element.send_keys(url)
	print("Putting url: " + url)

# установка условий
def set_conditions(ticker, condition, driver):
	driver.find_elements_by_class_name("icon-beK_KS0k")[5].click()
	driver.find_elements_by_class_name("tv-control-select__control-inner")[0].click()
	print("Setting conditions to " + str(condition))
	find_element_by_text_in_elements_class_name(condition, "tv-control-select__option-wrap", driver).click() # установка условия (trend, fli, tux)
	if condition_dict[condition] == 2 or condition_dict[condition] == 3:
		print("Setting 'times per bar'")
		sleep(1)
		driver.find_elements_by_class_name("tv-alert-dialog__button-caption")[1].click() # установка "раз за бар"
	# работа с webhook
	if len(driver.find_elements_by_class_name("tv-alert-dialog__fieldset-value-item--collapsed")) == 1:
		webhook(driver)
	else:
		driver.find_elements_by_class_name("tv-control-checkbox__ripple")[4].click()
		webhook(driver)
	driver.find_element_by_class_name("tv-button__loader").click()
	sleep(3)

# функция удаления оповещений
def remove_signals(ticker, driver):
	i = 0
	driver.implicitly_wait(2)
	driver.find_elements_by_class_name("button-3SuA46Ww")[5].click()
	driver.find_elements_by_class_name("button-3SuA46Ww")[1].click()
	driver.implicitly_wait(delay)
	sleep(1)
	if not check_exists_by_class_name("input-2O3idT5-", 2, driver):
		ActionChains(driver).move_to_element(driver.find_elements_by_class_name("icon-beK_KS0k")[4]).perform()
		driver.find_elements_by_class_name("icon-beK_KS0k")[4].click()
		driver.find_element_by_class_name("input-2O3idT5-").send_keys(ticker)
		sleep(1)
		count = len(driver.find_elements_by_class_name("item-2FogpcK6"))
		while i < count:
			element = driver.find_elements_by_class_name("item-2FogpcK6")[0]
			sleep(1)
			ActionChains(driver).move_to_element(driver.find_elements_by_class_name("attributes-3QRqSOpy")[0]).perform()
			ActionChains(driver).move_to_element(element).perform()
			driver.find_elements_by_class_name("button-GlaDWSuu")[3].click()
			driver.find_elements_by_class_name("tv-button__loader")[0].click()
			print("Signal deleted ")
			i += 1
			sleep(2)

# функция удаления котировок
def remove_quotation(ticker, driver):
	i = 0
	driver.implicitly_wait(2)
	driver.find_elements_by_class_name("button-3SuA46Ww")[5].click()
	driver.find_elements_by_class_name("button-3SuA46Ww")[0].click()
	driver.implicitly_wait(delay)
	sleep(1)
	while i < len(driver.find_elements_by_class_name("symbolNameText-2EYOR9jS")):
		element = driver.find_elements_by_class_name("symbolNameText-2EYOR9jS")[i]
		element.click()
		if element.text.lower().find(ticker) != -1 and element.text.lower().find(ticker) < 5:
			text = element.text
			actions = ActionChains(driver)
			actions.send_keys(Keys.DELETE)
			actions.perform()
			print("Quotation deleted " + text)
			i-=1
			sleep(2)
		i+=1

# функция установки котировки
def set_quotation(ticker, driver):
	driver.find_elements_by_class_name("button-3SuA46Ww")[5].click()
	driver.find_elements_by_class_name("button-3SuA46Ww")[0].click()
	driver.find_element_by_class_name("addSymbolButton-3UDa0bAV").click()
	driver.find_element_by_class_name("search-1t76YXcC").send_keys(ticker)
	driver.find_element_by_class_name("search-1t76YXcC").send_keys(Keys.ENTER)

# функция установки интервала времени
def define_interval(interval, driver):
	driver.find_element_by_class_name("value-DWZXOdoK").click()
	find_element_by_text_in_elements_class_name(interval, "label-3Xqxy756", driver).click()

# функция старта оповещения
def start_notification(ticker, driver):
	i = 0
	button_id = 0
	driver.implicitly_wait(2)
	driver.find_elements_by_class_name("button-3SuA46Ww")[5].click()
	driver.find_elements_by_class_name("button-3SuA46Ww")[1].click()
	# if check_exists_by_class_name("hidden", 2, driver):	
	# 	driver.find_elements_by_class_name("button-3SuA46Ww")[1].click()
	driver.implicitly_wait(delay)
	if not check_exists_by_class_name("input-2O3idT5-", 2, driver):
		driver.find_elements_by_class_name("icon-beK_KS0k")[4].click()
		driver.find_element_by_class_name("input-2O3idT5-").send_keys(ticker)
		sleep(1)
		while i < len(driver.find_elements_by_class_name("item-2FogpcK6")):
			element = driver.find_elements_by_class_name("item-2FogpcK6")[i]
			element.click()
			print(ticker + " started")
			driver.find_elements_by_class_name("button-2-lC3gh4")[1].click()
			i+=1
			button_id += 3	
			sleep(1)

# функция остановки оповещения
def stop_notification(ticker, driver):
	i = 0
	button_id = 0
	driver.implicitly_wait(2)
	driver.find_elements_by_class_name("button-3SuA46Ww")[5].click()
	driver.find_elements_by_class_name("button-3SuA46Ww")[1].click()
	# if check_exists_by_class_name("hidden", 2, driver):
	# 	driver.find_elements_by_class_name("button-3SuA46Ww")[1].click()
	driver.implicitly_wait(delay)
	if not check_exists_by_class_name("input-2O3idT5-", 2, driver):
		driver.find_elements_by_class_name("icon-beK_KS0k")[4].click()
		driver.find_element_by_class_name("input-2O3idT5-").send_keys(ticker)
		sleep(1)
		while i < len(driver.find_elements_by_class_name("item-2FogpcK6")):
			element = driver.find_elements_by_class_name("item-2FogpcK6")[i]
			element.click()
			print(ticker + " stopped")
			driver.find_elements_by_class_name("button-2-lC3gh4")[2].click()
			i+=1
			button_id += 3
			sleep(1)

def login(driver):
	print("Going to main page")
	driver.get("https://ru.tradingview.com/") # переход на сайт
	# логин
	print("Signing in")
	driver.find_element_by_class_name("tv-header__link--signin").click()
	driver.find_element_by_class_name("tv-signin-dialog__toggle-email").click()
	driver.find_element_by_name("username").send_keys(username)
	driver.find_element_by_name("password").send_keys(password)
	driver.find_element_by_class_name("tv-button__loader").click()
	sleep(1)

# основной код
try:
	# парсинг параметров
	ticker = args.ticker.lower() 
	condition = args.condition
	signals = args.signals
	remove = args.remove
	start = args.start
	stop = args.stop
	# установка настроек браузера
	options = Options()
	options.headless = args.headless # режим без открытия браузера(скрытый режим)
	driver = webdriver.Firefox(options=options)
	driver.implicitly_wait(delay)
	#driver.set_window_size(1280, 720)
	# начало работы
	login(driver)
	# режим запуска оповещений
	if start == True:
		start_notification(ticker, driver)
	elif stop == True:
		stop_notification(ticker, driver)
	# режим удаления
	elif remove == True:
		print("Removing signals")
		remove_signals(ticker, driver)
		print("Removing quotation")
		remove_quotation(ticker, driver)
	else:
		# ввод тикера
		print("Writing ticker: " + str(ticker))
		driver.find_element_by_name("query").send_keys(ticker)
		sleep(1)
		driver.find_element_by_name("query").send_keys(Keys.ENTER)
		driver.find_element_by_class_name("icon-1grlgNdV").click()
		driver.switch_to.window(driver.window_handles[1])
		# установка интервала в 1 час
		print("Setting interval 1 hour")
		define_interval(interval, driver)
		# установка котировки
		print("Setting quotation")
		set_quotation(ticker, driver)
		# установка условий
		if signals == True:
			for key in condition_dict:
				condition = key
				set_conditions(ticker, key, driver)
		else:
			set_conditions(ticker, condition, driver)
	print("Done!")
	driver.quit()
except KeyboardInterrupt:
	print("Interrupted")
	driver.quit()
	sys.exit()
except Exception as err:
	print("Error " + str(err))
	driver.quit()
	sys.exit()