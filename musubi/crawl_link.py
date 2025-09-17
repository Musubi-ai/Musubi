import os
import requests
from abc import ABC, abstractmethod
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from loguru import logger
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional
import orjson
import time
from tqdm import tqdm


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}


class BaseCrawl(ABC):
    def __init__(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.root_path = root_path
        self.pages = pages
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        self.sleep_time = sleep_time
        self.page_init_val = page_init_val
        self.multiplier = multiplier

    @abstractmethod
    def crawl_link(self):
        ...

    @abstractmethod
    def check_link_result(self):
        ...


class Scan(BaseCrawl):
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time, page_init_val, multiplier)
        if pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if suffix:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) + self.suffix for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) for i in range(self.pages)]

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
            if self.root_path:
                if self.plural_a_tag:
                    if "http" not in block["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block["href"]
                    else:
                        link = block["href"]
                else:
                    if "http" not in block.a["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block.a["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block.a["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block.a["href"]
                    else:
                        link = block.a["href"]
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
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        
        for i in tqdm(range(start_page, self.length), desc="Crawling urls..."):
            page = self.pages_lst[i]
            link_list = self.get_urls(page=page)
            for link in link_list:
                if url_list and link in url_list:
                    continue 
                dictt = {"link": link}
                with open(self.url_path, "ab") as file:
                    file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        page = self.pages_lst[0]
        link_list = self.get_urls(page=page)
        print(link_list[0])


class Scroll(BaseCrawl):
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = 5,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.scroll_time = pages

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
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        with tqdm(total=scroll_time, desc="Scrolling") as pbar:
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
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None
        self.browse_website()
        self.scroll()
        elements = self.driver.find_elements(By.TAG_NAME, self.block1[0])

        for item in elements:
            class_ = item.get_attribute("class")
            if (class_ == self.block1[1]):
                if self.block1[0] != "a":
                    a = item.find_element(By.TAG_NAME, "a")
                    url = a.get_attribute("href")
                else:
                    url = item.get_attribute("href")
                if self.root_path:
                    if self.root_path[-1] == url[0] == "/":
                        self.root_path = self.root_path[:-1]
                    elif (self.root_path[-1] != "/") and (url[0] != "/"):
                        self.root_path = self.root_path + "/"
                    elif ("http" in self.root_path) and ("http" in url):
                        self.root_path = ""
                    url = self.root_path + url
                if url_list and (url in url_list):
                    continue 
                dictt = {"link": url}

                with open(self.url_path, "ab") as file:
                    file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        self.browse_website()
        self.scroll(scroll_time = 1)
        element = self.driver.find_element(By.CLASS_NAME, self.block1[1])
        elements = element.find_elements(By.TAG_NAME, "a")

        check_list = []

        for item in elements:
            url = item.get_attribute("href")
            if self.root_path:
                url = self.root_path + url
            dictt = {"link": url}
            check_list.append(dictt)
        print(check_list)


class OnePage(BaseCrawl):
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")

    def get_urls(self):
        link_list = []
        r = requests.get(self.prefix, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")

        if self.block2:
            blocks = soup.find(self.block1[0], class_=self.block1[1])
            blocks = blocks.find_all(self.block2[0], class_=self.block2[1])
        else:
            blocks = soup.find_all(self.block1[0], class_=self.block1[1])

        for block in blocks:
            if self.root_path:
                if self.plural_a_tag:
                    if "http" not in block["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block["href"]
                    else:
                        link = block["href"]
                else:
                    if "http" not in block.a["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block.a["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block.a["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block.a["href"]
                    else:
                        link = block.a["href"]
            else:
                if self.plural_a_tag:
                    link = block["href"]
                else:
                    link = block.a["href"]
            link_list.append(link)

        return link_list
    
    def crawl_link(self):
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        link_list = self.get_urls()
        for link in link_list:
            if url_list and link in url_list:
                continue 
            dictt = {"link": link}
            with open(self.url_path, "ab") as file:
                file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        link_list = self.get_urls()
        print(link_list)


class Click(BaseCrawl):
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = 5,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.click_time = pages

    def browse_website(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = Edge(options=options)
        self.driver.get(self.prefix)
        if self.sleep_time:
            time.sleep(self.sleep_time)

    def crawl_link(
        self,
        click_time: int = None,
    ):
        self.browse_website()
        n = 0
        click_time = click_time if click_time is not None else self.click_time

        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        with tqdm(total=click_time, desc="Clicking") as pbar:
            while n < click_time:
                elements = self.driver.find_elements(By.CLASS_NAME, self.block1[1])

                for item in elements:
                    item = item.find_element(By.TAG_NAME, "a")
                    url = item.get_attribute("href")
                    if self.root_path:
                        if self.root_path[-1] == url[0] == "/":
                            self.root_path = self.root_path[:-1]
                        elif (self.root_path[-1] != "/") and (url[0] != "/"):
                            self.root_path = self.root_path + "/"
                        elif ("http" in self.root_path) and ("http" in url):
                            self.root_path = ""
                        url = self.root_path + url
                    if url_list and url in url_list:
                        continue 
                    dictt = {"link": url}

                    with open(self.url_path, "ab") as file:
                        file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

                button = self.driver.find_element("xpath", self.block2[1])
                try:
                    self.driver.execute_script("$(arguments[0]).click()", button)
                except:
                    try:
                        button.click()
                    except:
                        logger.warning("Reach click limit or finish clicking.")
                n += 1
                if self.sleep_time:
                    time.sleep(self.sleep_time)
                pbar.update(1)

    def check_link_result(
        self,
        click_time: int = 5,
    ):
        link_list = []
        self.browse_website()
        n = 0
        click_time = click_time if click_time is not None else self.click_time

        with tqdm(total=click_time, desc="Clicking") as pbar:
            while n < click_time:
                elements = self.driver.find_elements(By.CLASS_NAME, self.block1[1])

                for item in elements:
                    item = item.find_element(By.TAG_NAME, "a")
                    url = item.get_attribute("href")
                    if self.root_path:
                        if self.root_path[-1] == url[0] == "/":
                            self.root_path = self.root_path[:-1]
                        elif (self.root_path[-1] != "/") and (url[0] != "/"):
                            self.root_path = self.root_path + "/"
                        elif ("http" in self.root_path) and ("http" in url):
                            self.root_path = ""
                        url = self.root_path + url
                    link_list.append(url)

                button = self.driver.find_element("xpath", self.block2[1])
                try:
                    self.driver.execute_script("$(arguments[0]).click()", button)
                except:
                    try:
                        button.click()
                    except:
                        logger.warning("Reach click limit or finish clicking.")
                n += 1
                if self.sleep_time:
                    time.sleep(self.sleep_time)
                pbar.update(1)
        print(link_list)