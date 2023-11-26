'''
return data = [{'title': '', 'page': '', 'author': '', 'author_stat': '', 'timestamp': '', 'content': '', 'url': ''},
               {'title': '', 'page': '', 'author': '', 'author_stat': '', 'timestamp': '', 'content': '', 'url': ''},
               {'title': '', 'page': '', 'author': '', 'author_stat': '', 'timestamp': '', 'content': '', 'url': ''}]
'''

'''
<<--Caution-->> Use a VPN service to crawl the deep web.
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import time
import json
import os

class Crawler:
    def __init__(self):
        self.driver = Driver()
        self.breachforums = Breachforums(self.driver)
    
    def start(self):
        data = []
        
        self.breachforums.page_set()
        for page in range(1, self.breachforums.page_max + 1):
            print(f'\n[{page}/{self.breachforums.page_max} PAGE]*******************************************************')
            data += self.breachforums.crawl_posts(page)

        self.driver.close()

        deduplication = Deduplication()
        deduplication.save_data(data)

        return data 


class Driver:
    def __init__(self, option='visible'):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.add_argument("--log-level=0")      
        if option == 'hidden':
           self.options.add_argument("headless")
           self.options.add_argument("disable-gpu")
        
        self.driver = webdriver.Chrome(options=self.options)

    def get(self, url):
        #print(url)
        return self.driver.get(url)

    def page_source(self):
        return self.driver.page_source
    
    def execute_script(self, script):
        return self.driver.execute_script(script)

    def find_elements_by_css_selector(self, selector):
        return self.driver.find_elements(By.CSS_SELECTOR, selector)
    
    def close(self): 
        self.driver.close()


class Breachforums:
    def __init__(self, driver):
        self.driver = driver
        self.deduplication = Deduplication()
        self.url = 'https://breachforums.is/Forum-Other-Leaks'
        self.page_max = 0
    
    def page_set(self):
        self.driver.get(self.url)

        WebDriverWait(self.driver.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pages'))
        )
        page_html = self.driver.page_source()
        soup = BeautifulSoup(page_html, 'html.parser')
        pages_element = soup.select_one('.pages')

        pages_text = pages_element.get_text(strip=True)
        self.page_max = int(pages_text.split('(')[1].split(')')[0])
    
    def crawl_posts(self, page):
        page_url = f'{self.url}?page={page}'
        self.driver.get(page_url)
        
        WebDriverWait(self.driver.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.tborder.clear'))
        )

        elements = '.trow2.forumdisplay_regular .subject_old a, .trow2.forumdisplay_regular .subject_new a, .trow1.forumdisplay_regular .subject_new a, .trow1.forumdisplay_regular .subject_old a'
        post_links = WebDriverWait(self.driver.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, elements))
        )

        data = []
        for index, post_link in enumerate(post_links):
            is_url = 0
            post = post_link.get_attribute('href')
            post_url = post
            print(f'[{index+1}/{len(post_links)}] {post}')

            if self.deduplication.is_log_file():
                log_data = self.deduplication.load_data()

            try:
                if log_data:
                    for url in log_data:
                        if post_url in url.get('url', ''):
                            is_url = 1
            except UnboundLocalError:
                pass
            
            if is_url == 0:
                post_link.click()

                WebDriverWait(self.driver.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'thread-info__thread'))
                )

                post_html = self.driver.page_source()
                post_soup = BeautifulSoup(post_html, 'html.parser')

                title = post_soup.select_one('.thread-info__name').get_text(strip=True)
                timestamp = post_soup.select_one('.thread-info__datetime').get_text(strip=True)
            
                WebDriverWait(self.driver.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'post'))
                )

                post_html = self.driver.page_source()
                post_soup = BeautifulSoup(post_html, 'html.parser')

                author = post_soup.select_one('.post__user-profile').get_text(strip=True)
                author_stat = post_soup.select_one('.post__author-stats').get_text(strip=True)
                content = post_soup.select_one('.post_content').get_text(strip=True)
            
                data.append({'title': title, 'page': page, 'author': author, 'author_stat': author_stat, 'timestamp': timestamp, 'content': content, 'url': post_url})

                self.driver.execute_script("window.history.go(-1)")

                WebDriverWait(self.driver.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.tborder.clear'))
                )
            
            else:
                pass

        return data
            

class Deduplication:
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), 'log_data.json')

    def is_log_file(self):
        return os.path.isfile(self.file_path)
    
    def save_data(self, data):
        mod = 'a'
        if data:
            if not os.path.isfile(self.file_path):
                mod = 'w'
            with open(self.file_path, mod) as file:
                json.dump(data, file, indent=2)
            print("File creation completed.")
        else:
            print("No data to create.")
    
    def load_data(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as file:
                file_data = json.load(file)
            return file_data
        else:
            print(f"'{self.file_path}' does not exist.")
            return None
    
    def delete(self, answer):
        if answer:
            try:
                os.remove(self.file_path)
                print("")
            except FileNotFoundError:
                print(f"'{self.file_path}' does not exist.")
            except Exception as e:
                print(f'Error: {e}')


if __name__ == "__main__":
    start_time = time.time()

    crawler = Crawler()
    data = crawler.start()

    for item in data:
        print(item)
    
    end_time = time.time()
    print("time:", (end_time - start_time))