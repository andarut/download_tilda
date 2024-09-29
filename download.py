import os
import time
from bs4 import BeautifulSoup

import os
import time
import inspect # for debug
import filecmp # for chunk diff

import selenium
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Logger:

	class Colors:
		HEADER = '\033[95m'
		BLUE = '\033[94m'
		CYAN = '\033[96m'
		GREEN = '\033[92m'
		YELLOW = '\033[93m'
		RED = '\033[91m'
		END = '\033[0m'
		BOLD = '\033[1m'
		UNDERLINE = '\033[4m'

	def print(self, text, color):
		print("[" + inspect.stack()[2].function.capitalize() + "]: " + color + text + self.Colors.END)

	def log(self, log_text):
		self.print(log_text, self.Colors.CYAN)

	def error(self, error_text):
		self.print(error_text, self.Colors.RED)

	def warning(self, warning_text):
		self.print(warning_text, self.Colors.YELLOW)

	def ok(self, ok_text):
		self.print(ok_text, self.Colors.GREEN)

class Engine:

	ACTION_TIMEOUT = 5
	STARTUP_TIMEOUT = 5

	class Element:

		def __init__(self, name: str, xpath: str):
			self.name = name
			self.xpath = xpath
			self.selenium_element = WebElement(None, None)
			self.logger = Logger()

		def text(self, value_type=str):
			# TODO: rewrite
			if value_type == str:
				return self.selenium_element.text

			try:
				if value_type == int:
					return int(self.selenium_element.text)
			except TypeError:
				self.logger.error(f"{self.name} text is {self.selenium_element.text}, not {value_type}")
				exit(1)

		def click(self):
			self.selenium_element.click()

		def type(self, text: str, erase=False, enter=False):
			if erase:
				old_text = self.text()
				for _ in range(len(old_text)):
					self.selenium_element.send_keys(Keys.BACKSPACE)

			self.selenium_element.send_keys(text)

			if enter:
				self.selenium_element.send_keys(Keys.ENTER)

	def __init__(self, url:str, debug=False):
		self.url = url
		self.logger = Logger()
		self.options = webdriver.ChromeOptions()
		self.options.add_argument("--mute-audio")
		self.DEBUG = debug

	def start(self):
		self.driver = webdriver.Chrome(options=self.options)
		self.driver.get(self.url)
		time.sleep(self.STARTUP_TIMEOUT)

	def find_element(self, name: str, xpath: str) -> Element:
		element = self.Element(name, xpath)

		try:
			element.selenium_element = self.driver.find_element(By.XPATH, element.xpath)
		except selenium.common.exceptions.NoSuchElementException:
			self.logger.error(f"{element.name} not found")
			exit(1)

		if self.DEBUG:
			self.logger.log(f"{element.name} found")

		return element

	def download(self, path):
		# get all urls (all resources)
		urls = []
		for request in self.driver.requests:
			if request.url != self.url:
				urls.append(request.url)

		# save source code
		data = self.driver.page_source

		self.quit()

		# download all resources
		for url in urls:
			url_path = os.path.basename(url).split('?')[0]
			if len(url_path) > 0:
				# print(f'curl "{url}" -o "{url_path}"')
				os.system(f'curl -q "{url}" -o "{url_path}"')
				if url not in data:
					url = f"{url}".replace(self.url, "")
					print(url, url_path)
				data = data.replace(url, url_path)

		print(path)
		with open(path, "w+") as f:
			f.write(data)

		# os.system(f"open {path}")


	def find_elements(self, name: str, class_name: str) -> [Element]:
		elements = []

		try:
			for el in self.driver.find_elements(By.CLASS_NAME, class_name):
				element = self.Element(name, "")
				element.selenium_element = el
				elements.append(element)
		except selenium.common.exceptions.NoSuchElementException:
			self.logger.error(f"{name} not found")
			exit(1)

		if self.DEBUG:
			self.logger.log(f"{name} found {len(elements)} times")

		return elements

	def click(self, element: Element):
		element.click()
		if self.DEBUG:
			self.logger.log(f"{element.name} clicked")
		time.sleep(self.ACTION_TIMEOUT)

	def type(self, element: Element, text: str, erase=False, enter=False):
		element.type(text, erase, enter)
		if self.DEBUG:
			self.logger.log(f"{element.name} typed {text} with erase={erase}, enter={enter}")
		time.sleep(self.ACTION_TIMEOUT)

	def quit(self):
		self.driver.quit()

def download(url, path=''):
	engine = Engine(url, True)
	engine.start()
	engine.download(path)


URL = "https://afs1.tilda.ws"

download(URL, "index.html")
