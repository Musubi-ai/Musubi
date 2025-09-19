import os
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional
import orjson
import random
import aiohttp
import asyncio
from loguru import logger
from tqdm import tqdm
from .utils import get_root_path


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

class AsyncScan:
    def __init__(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
        max_concurrent_tasks: int = 30,
        **kwargs
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.root_path = root_path
        self.pages = pages
        self.page_init_val = page_init_val
        self.multiplier = multiplier
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        if pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if suffix:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) + self.suffix for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) for i in range(self.pages)]
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
                            if "http" in block["href"]:
                                link = block["href"]
                            else:
                                root_path = get_root_path(page)
                                if block["href"][0] == "/":
                                    link = root_path + block["href"]
                                else:
                                    link = root_path + "/" + block["href"]
                        else:
                            if "http" in block.a["href"]:
                                link = block.a["href"]
                            else:
                                root_path = get_root_path(page)
                                if block.a["href"][0] == "/":
                                    link = root_path + block.a["href"]
                                else:
                                    link = root_path + "/" + block.a["href"]
                    link_list.append(link)

            except Exception as e:
                logger.error(f"Error fetching {page}: {e}")

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

            with tqdm(total=len(tasks), desc="Crawling urls") as pbar:
                for task in asyncio.as_completed(tasks):
                    link_list = await task
                    for link in link_list:
                        if url_list and link in url_list:
                            continue
                        dictt = {"link": link}
                        with open(self.url_path, "ab") as file:
                            file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")
                    pbar.update(1)


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