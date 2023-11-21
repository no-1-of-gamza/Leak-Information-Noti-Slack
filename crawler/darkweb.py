from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import abc
import time
import random


class Crawler:
	def __init__(self):
		self.driver = Driver()
		self.lockbit = LockBit(self.driver.get())

	def start(self) -> list:
		data = []
		data += self.lockbit.start()

		return data


class Driver:
	def __init__(self):
		proxy = "127.0.0.1:9150"
		options = webdriver.ChromeOptions()
		options.add_experimental_option("excludeSwitches", ["enable-logging"])
		options.add_argument('--proxy-server=socks5://'+proxy)

		self.driver = webdriver.Chrome(options=options)

	def get(self):
		return self.driver

	def close(self):
		self.driver.close()


class LeakCrawler(abc.ABC):
	def __init__(self, driver):
		self.driver = driver
		self.site = []

	def get_source(self):
		self.driver.get(url=self.get_random_host())
		self.bypassProtection()

		source = self.driver.page_source
		return source

	@abc.abstractmethod
	def get_random_host(self) -> str:
		pass

	@abc.abstractmethod
	def bypassProtection(self):
		pass


class LockBit(LeakCrawler):
	def __init__(self, driver):
		super(LockBit, self).__init__(driver)
		self.driver = driver
		self.site = [
			"http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion",
			"http://lockbitapt2yfbt7lchxejug47kmqvqqxvvjpqkmevv4l3azl3gy6pyd.onion",
			"http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion",
			"http://lockbitapt34kvrip6xojylohhxrwsvpzdffgs5z4pbbsywnzsbdguqd.onion",
			"http://lockbitapt5x4zkjbcqmz6frdhecqqgadevyiwqxukksspnlidyvd7qd.onion"
		]

	def get_random_host(self):
		idx = random.randint(0, len(self.site)-1)
		return self.site[idx]

	def start(self):
		source = self.get_source()
		data = self.crawl_site(source)
		return data

	def bypassProtection(self):
		WebDriverWait(self.driver, 20).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'post-big-list'))
		)

	def crawl_site(self, source):
		data = []

		soup = BeautifulSoup(source, "html.parser")
		data += self.crawl_posts(soup)
		for d in data:
			self.crawl_details(d, d["url"])

		return data

	def crawl_posts(self, soup):
		data = []

		items = soup.select("div.post-big-list>div.post-block")
		for item in items:
			domain = self.domain_parser(item.select_one("div.post-title").text)
			url = self.url_parser(item.get("onclick"))
			remain_timer = item.select_one("div.timer")
			remain_time = { "status": "pending" }
			try:
				remain_time["days"] = remain_timer.select_one("span.days").text
				remain_time["hours"] = remain_timer.select_one("span.hours").text
				remain_time["minutes"] = remain_timer.select_one("span.minutes").text
				remain_time["seconds"] = remain_timer.select_one("span.seconds").text
			except AttributeError:
				remain_time["status"] = "published"

			data.append({
				"domain": domain,
				"url": url,
				"remain_time": remain_time
			})

		return data

	def domain_parser(self, string):
		trim_string = string[2:]
		return trim_string.strip()

	def url_parser(self, string):
		path = string.strip()[11:-3]
		url = self.get_random_host() + path
		return url

	def crawl_details(self, post_data, url):
		self.driver.get(url=url)

		WebDriverWait(self.driver, 20).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'post-company-info'))
		)
		soup = BeautifulSoup(self.driver.page_source, "html.parser")

		deadline = soup.select_one("div.post-wrapper>p.post-banner-p").text
		
		company_info = soup.select_one("div.post-company-info")
		try:
			logo = company_info.select_one("div.post-company-img>img").get("src")
		except AttributeError:
			logo = ""
		try:
			description = company_info.select_one("div.post-company-content>div.desc").text
		except AttributeError:
			description = ""
		
		uploaded_updated_date = company_info.select_one("div.post-company-content>div.uploaded-updated-date")
		uploaded_date = uploaded_updated_date.select_one("div.uploaded-date>div.uploaded-date-utc").text
		updated_date = uploaded_updated_date.select_one("div.updated-date>div.updated-date-utc").text

		post_data["deadline"] = deadline
		post_data["logo"] = logo
		post_data["description"] = description
		post_data["uploaded_date"] = uploaded_date
		post_data["updated_date"] = updated_date


if __name__ == "__main__":
	crawler = Crawler()
	data = crawler.start()

	for d in data:
		print(d)
		print()