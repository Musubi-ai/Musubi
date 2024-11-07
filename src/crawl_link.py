import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List
import json
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
                link = self.prefix3 + block.a["href"]
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
                    return 
                dictt = {"link": link}
                with open(self.url_path, "a+", encoding="utf-8") as file:
                    file.write(json.dumps(dictt, ensure_ascii=False) + "\n")

    def check_link_reslt(self):
        page = self.pages_lst[0]
        link_list = self.get_urls(page=page)
        print(link_list[0])


if __name__ == "__main__":
    prefix =  "https://aroundtaiwan.net/category/go/page/"
    prefix2 = "/"
    prefix3 = None
    pages = 6
    block1 = ["div", "entries"]
    block2 = ["h2", "entry-title"]
    url_path = "test.json"
    scan = Scan(prefix, prefix2, prefix3, pages, block1, block2, url_path)
    # scan.check_link_reslt()
    scan.crawl_link()
    



