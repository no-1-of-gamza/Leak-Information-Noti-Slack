from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import abc
import random
from datetime import datetime, timezone

from darkweb_query import *


class Crawler:
	def __init__(self):
		self.driver = Driver()
		self.lockbit = LockBit(self.driver.get())

	def start(self) -> list:
		alarm_data = []

		result, rows = check_initialization()
		if len(rows) < 1:
			alarm_data += self.initial_launch()
		else:
			last_domain = rows[0][0]
			alarm_data += self.regular_launch(last_domain)

		self.close()
		return alarm_data

	def initial_launch(self):
		alarm_data = []

		crawl_data = self.lockbit.crawl_posts()
		for data in crawl_data:
			if data["status"] == "published":
				continue

			self.lockbit.crawl_details(data)
			alarm_data.append(data)

		for data in alarm_data:
			result, err = insert_pending(data)
			if not result:
				print(err)
				return []

		result, err = update_last_scan(crawl_data[0]["domain"])
		if not result:
			print(err)
			return []

		return alarm_data

	def regular_launch(self, last_domain):
		alarm_data = []

		crawl_data = self.lockbit.crawl_posts()
		i = 0
		while True:
			data = crawl_data[i]
			if data["domain"] == last_domain:
				break

			self.lockbit.crawl_details(data)
			alarm_data.append(data)
			i += 1

		result, rows = select_all_pending()
		if not result:
			print(err)
			return []

		for pending_data in rows:
			target_domain = pending_data[0]
			crawled_data = self.search_data(target_domain, crawl_data)
			if crawled_data == {}:
				data = self.create_negotiated_data(pending_data)
				alarm_data.append(data)

				result, err = delete_post(target_domain)
				if not result:
					print(err)
					return []
			elif crawled_data["status"] == "published":
				self.lockbit.crawl_details(crawled_data)
				alarm_data.append(crawled_data)

				result, err = delete_post(target_domain)
				if not result:
					print(err)
					return []

		result, err = update_last_scan(crawl_data[0]["domain"])
		if not result:
			print(err)
			return []

		return alarm_data

	def search_data(self, target_domain, crawl_data):
		for data in crawl_data:
			if data["domain"] == target_domain:
				return data
		return {}

	def create_negotiated_data(self, row) -> dict:
		data = {
			"domain": row[0],
			"url": row[1],
			"status": "negotiated",
			"remain_time": "",
			"deadline": row[3],
			"description": row[4],
			"uploaded_date": row[5],
			"updated_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
		}
		return data

	def close(self):
		self.driver.close()
		db_close()


class Driver:
	def __init__(self, option="visible"):
		proxy = "127.0.0.1:9150"

		self.options = webdriver.ChromeOptions()
		self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
		self.options.add_argument("--log-level=0")
		self.options.add_argument('--proxy-server=socks5://'+proxy)
		if option == "hidden":
			self.options.add_argument("headless")
			self.options.add_argument("disable-gpu")

		self.driver = webdriver.Chrome(options=self.options)

	def get(self):
		return self.driver

	def close(self):
		self.driver.close()


class LeakCrawler(abc.ABC):
	def __init__(self, driver):
		self.driver = driver
		self.site = ""

	def get_source(self):
		self.driver.get(url=self.site)
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
		self.site = self.get_random_host()

	def get_random_host(self):
		hosts = [
			"http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion",
			"http://lockbitapt2yfbt7lchxejug47kmqvqqxvvjpqkmevv4l3azl3gy6pyd.onion",
			"http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion",
			"http://lockbitapt34kvrip6xojylohhxrwsvpzdffgs5z4pbbsywnzsbdguqd.onion",
			"http://lockbitapt5x4zkjbcqmz6frdhecqqgadevyiwqxukksspnlidyvd7qd.onion"
		]

		idx = random.randint(0, len(hosts)-1)
		return hosts[idx]

	def bypassProtection(self):
		WebDriverWait(self.driver, 20).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'post-big-list'))
		)

	def crawl_posts(self):
		source = self.get_source()
		soup = BeautifulSoup(source, "html.parser")

		data = []
		items = soup.select("div.post-big-list>div.post-block")
		for item in items:
			domain = self.domain_parser(item.select_one("div.post-title").text)
			url = self.url_parser(item.get("onclick"))
			remain_timer = item.select_one("div.timer")
			status = "pending"
			remain_time = ""
			try:
				days = remain_timer.select_one("span.days").text
				hours = remain_timer.select_one("span.hours").text
				minutes = remain_timer.select_one("span.minutes").text
				seconds = remain_timer.select_one("span.seconds").text
				remain_time = "{} {} {} {}".format(days, hours, minutes, seconds)
			except AttributeError:
				status = "published"

			data.append({
				"domain": domain,
				"url": url,
				"status": status,
				"remain_time": remain_time
			})

		return data

	def domain_parser(self, string):
		trim_string = string[2:]
		return trim_string.strip()

	def url_parser(self, string):
		path = string.strip()[11:-3]
		url = self.site + path
		return url

	def crawl_details(self, post_data):
		self.driver.get(url=post_data["url"])

		WebDriverWait(self.driver, 40).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'post-company-info'))
		)
		soup = BeautifulSoup(self.driver.page_source, "html.parser")

		deadline = soup.select_one("div.post-wrapper>p.post-banner-p").text
		deadline = self.deadline_parser(deadline)
		
		company_info = soup.select_one("div.post-company-info")
		try:
			description = company_info.select_one("div.post-company-content>div.desc").text
			description = description[2:].strip()
		except AttributeError:
			description = ""
		
		uploaded_updated_date = company_info.select_one("div.post-company-content>div.uploaded-updated-date")
		uploaded_date = uploaded_updated_date.select_one("div.uploaded-date>div.uploaded-date-utc").text.strip()
		uploaded_date = self.date_parser(uploaded_date)
		updated_date = uploaded_updated_date.select_one("div.updated-date>div.updated-date-utc").text.strip()
		updated_date = self.date_parser(updated_date)

		post_data["deadline"] = deadline
		post_data["description"] = description
		post_data["uploaded_date"] = uploaded_date
		post_data["updated_date"] = updated_date

	def deadline_parser(self, string):
		deadline_string = string[10:-4].strip()

		date_format = "%d %b, %Y %H:%M:%S"
		date_obj = datetime.strptime(deadline_string, date_format)
		date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
		return date

	def date_parser(self, string):
		date_string = string[:-3].strip()

		date_format = "%d %b, %Y %H:%M"
		date_obj = datetime.strptime(date_string, date_format)
		date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
		return date


if __name__ == "__main__":
	crawler = Crawler()
	alarm_data = crawler.start()

	print("\n\nalarm data:", len(alarm_data))
	for d in alarm_data:
		print(d)
		print()
