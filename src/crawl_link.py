import os
import requests
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup
from typing import List
import json
import time
from tqdm import tqdm

headers = {'user-agent': 'Mozilla/5.0'}


class Scan():
    def __init__(
        self,
        prefix: str = None,
        prefix2: str = None,
        prefix3: str = None,
        pages: int = None,
        block1: List[str] = None,
        block2: List[str] = None,
        url_path: str = None
    ):
        self.prefix = prefix
        self.prefix2 = prefix2
        self.prefix3 = prefix3
        self.pages = pages
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        if pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if prefix2:
                self.pages_lst = [self.prefix + str(i+1) + self.prefix2 for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str(i+1) for i in range(self.pages)]

        self.length = len(self.pages_lst)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")

    def get_urls(self, page):
        link_list = []
        r = requests.get(page, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")

        if self.block2:
            blocks = soup.find(self.block1[0], class_=self.block1[1])
            blocks = blocks.find_all(self.block2[0], class_=self.block2[1])
        else:
            blocks = soup.find_all(self.block1[0], class_=self.block1[1])

        for block in blocks:
            if self.prefix3:
                if self.plural_a_tag:
                    link = self.prefix3 + block["href"]
                else:
                    link = self.prefix3 + block.a["href"]
            else:
                if self.plural_a_tag:
                    link = block["href"]
                else:
                    link = block.a["href"]
            link_list.append(link)

        return link_list
    
    def crawl_link(self, start_page: int=0):
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True)["link"].to_list()
        else:
            url_list = None

        for i in tqdm(range(start_page, self.length)):
            page = self.pages_lst[i]
            link_list = self.get_urls(page=page)
            for link in link_list:
                if url_list and link in url_list:
                    continue 
                dictt = {"link": link}
                with open(self.url_path, "a+", encoding="utf-8") as file:
                    file.write(json.dumps(dictt, ensure_ascii=False) + "\n")

    def check_link_reslt(self):
        page = self.pages_lst[0]
        link_list = self.get_urls(page=page)
        print(link_list[0])


class Scroll:
    def __init__(
        self,
        prefix: str = None,
        prefix2: str = None,
        prefix3: str = None,
        pages: int = None,
        block1: List[str] = None,
        block2: List[str] = None,
        url_path: str = None,
        sleep_time: int = 3,
    ):
        self.prefix = prefix
        self.prefix2 = prefix2
        self.prefix3 = prefix3
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        self.sleep_time = sleep_time
        self.scroll_time = pages
        self.url_path = url_path

    def browse_website(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = Edge(options=options)
        self.driver.get(self.prefix)
        time.sleep(self.sleep_time)

    def scroll(
        self,
        scroll_time: int = None
    ):
        n = 0
        scroll_time = scroll_time if scroll_time is not None else self.scroll_time
        pbar = tqdm(total = scroll_time)
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while n < scroll_time:
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            n += 1
            time.sleep(self.sleep_time)
            pbar.update(1)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def crawl_link(self):
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True)["link"].to_list()
        else:
            url_list = None
        self.browse_website()
        self.scroll()
        element = self.driver.find_element(By.CLASS_NAME, self.block1[1])
        elements = element.find_elements(By.TAG_NAME, "a")

        for item in elements:
            url = item.get_attribute("href")
            if self.prefix3:
                url = self.prefix3 + url
            if url_list and url in url_list:
                continue 
            dictt = {"link": url}

            with open(self.url_path, "a+", encoding="utf-8") as file:
                file.write(json.dumps(dictt, ensure_ascii=False) + "\n")

    def check_link_result(self):
        self.browse_website()
        self.scroll(scroll_time = 1)
        element = self.driver.find_element(By.CLASS_NAME, self.block1[1])
        elements = element.find_elements(By.TAG_NAME, "a")

        check_list = []

        for item in elements:
            url = item.get_attribute("href")
            if self.prefix3:
                url = self.prefix3 + url
            dictt = {"link": url}
            check_list.append(dictt)
        
        print(check_list)


if __name__ == "__main__":
    prefix =  "https://www.popdaily.com.tw/explore/press"
    prefix2 = None
    prefix3 = None
    pages = 5
    block1 = ["div", "DesktopGridContainer-sc-1eawaw9-0.cutvQW"]
    block2 = None
    url_path = "test.json"
    # scan = Scan(prefix, prefix2, prefix3, pages, block1, block2, url_path)
    # scan.check_link_reslt()
    # scan.crawl_link()
    scroll = Scroll(prefix, prefix2, prefix3, pages, block1, block2, url_path)
    # scroll.check_link_result()
    scroll.crawl_link()    
