import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List
import json
import random
import aiohttp
import asyncio
from rich.progress import SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, Progress, MofNCompleteColumn, TimeElapsedColumn


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}

progress = Progress(
    SpinnerColumn(spinner_name="aesthetic"),
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn(),
    BarColumn(bar_width=200),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
)


class AsyncScan:
    def __init__(
        self,
        prefix: str = None,
        suffix: str = None,
        root_path: str = None,
        pages: int = None,
        block1: List[str] = None,
        block2: List[str] = None,
        url_path: str = None,
        max_concurrent_tasks: int = 10,
        **kwargs
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.root_path = root_path
        self.pages = pages
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        if pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if suffix:
                self.pages_lst = [self.prefix + str(i+1) + self.suffix for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str(i+1) for i in range(self.pages)]

        self.length = len(self.pages_lst)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")

    async def fetch(self, session: aiohttp.ClientSession, url):
        async with session.get(url, headers=headers) as response:
            return await response.text()
        
    async def get_urls(
        self, 
        session: aiohttp.ClientSession = None, 
        page: str = None
    ):
        async with self.semaphore:
            link_list = []
            try:
                html = await self.fetch(session, page)
                soup = BeautifulSoup(html, features="html.parser")

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

            except Exception as e:
                print(f"Error fetching {page}: {e}")

            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            return link_list
    
    async def crawl_link(self, start_page: int = 0):
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(start_page, self.length):
                page = self.pages_lst[i]
                tasks.append(self.get_urls(session, page))

            with progress:
                for task in progress.track(asyncio.as_completed(tasks), total=len(tasks), description="Crawling urls"):
                    link_list = await task
                    for link in link_list:
                        if url_list and link in url_list:
                            continue
                        dictt = {"link": link}
                        with open(self.url_path, "a+", encoding="utf-8") as file:
                            file.write(json.dumps(dictt, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    prefix = "https://aroundtaiwan.net/category/go/page/"
    suffix = "/"
    root_path = None
    pages = 6
    block1 = ["div", "entries"]
    block2 = ["h2", "entry-title"]
    url_path = "test.json"
    
    scan = AsyncScan(prefix, suffix, root_path, pages, block1, block2, url_path)
    asyncio.run(scan.crawl_link())