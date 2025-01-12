import os
import requests
from bs4 import BeautifulSoup
import pymupdf
import pymupdf4llm
import io
import re
from trafilatura import fetch_url, extract
import json
from tqdm import tqdm
import pandas as pd
import time
import aiohttp
import asyncio


headers = {'user-agent': 'Mozilla/5.0'}


def formate_pdf(pdf_content: str):
    text_list = pdf_content.split("\n")
    length = len(text_list)

    formated_doc = ""

    for i in range(length):
        line = text_list[i]
        if (len(line) == 0) or (len(line.replace(" ", "")) == 0):
            continue
        if re.search("([一二三四五六七八九十]、\s\w*)|([123456789].\s\w*)|([零壹貳參肆伍陸柒捌玖拾]、\s\w*)|([一二三四五六七八九十]、\w*)|([零壹貳參肆伍陸柒捌玖拾]、\w*)", line):
            line = "\n" + line + "\n" if i != 0 else line + "\n"
        if line[-1] in ["。", "：", ":", "？", "?", ".", "」", ")", "|", "`", "-", "》"]:
            line = line + "\n"
        if line[0] == "#" and line[-1] != "\n":
            line = line + "\n"
        if len(line) - len(line.lstrip()) > 0:
            line = line.lstrip()
        formated_doc += line

    return formated_doc


async def get_content(url: str = None, session: aiohttp.ClientSession = None):
    if url.endswith(".pdf"):
        async with session.get(url, headers=headers) as request:
            filestream = io.BytesIO(await request.read())
        with pymupdf.open(stream=filestream.getvalue(), filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
        result = formate_pdf(result)
    else:
        loop = asyncio.get_event_loop()
        downloaded = await loop.run_in_executor(None, fetch_url, url)
        result = await loop.run_in_executor(None, extract, downloaded, True, "markdown")
    return result

async def fetch(session: aiohttp.ClientSession, url):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def get_image_text_pair(
    url: str = None,
    img_txt_block: list = None
):
    async with aiohttp.ClientSession() as session:
        content = await fetch(session, url)
        soup = BeautifulSoup(content, "html.parser")
        soup = soup.find(img_txt_block[0], class_=img_txt_block[1])
        img_list = []
        for img_tag in soup.find_all("img"):
            img_url = img_tag.get("src")
            description = img_tag.get("alt")
            img_list.append({"img_url": img_url, "caption": description, "url": url})
        return img_list


class AsyncCrawl():
    """
    Args:
        crawl_type (`str`) should be one of 'text' or 'img-text' 
    """
    def __init__(
        self,
        url_path: str = None,
        crawl_type: str = None,
        max_concurrent_tasks: int = 10,
    ):
        self.url_path = url_path
        self.crawl_type = crawl_type     
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def check_content_result(
        self,
        img_txt_block: list = None
    ):
        """
        Check the content of the first website in urls_path.
        """
        df = pd.read_json(self.url_path, lines=True)
        url = df.iloc[0]["link"]
        if self.crawl_type == "text":
            res = await get_content(url=url)
        elif self.crawl_type == "img-text":
            res = await get_image_text_pair(url=url, img_txt_block=img_txt_block)
        print(res)

    async def crawl_contents(
        self, 
        start_idx: int = 0, 
        save_path: str = None,
        sleep_time: int = None,
        img_txt_block: list = None
    ):
        async with self.semaphore:
            save_file = os.path.isfile(save_path)
            content_list = pd.read_json(save_path, lines=True)["url"].to_list() if save_file else None
            url_df = pd.read_json(self.url_path, lines=True)
            tasks = []

            for i in range(start_idx, len(url_df)):
                link = url_df.iloc[i]["link"]
                if content_list and link in content_list:
                    continue

                if self.crawl_type == "text":
                    tasks.append(get_content(url=link))
                elif self.crawl_type == "img-text":
                    tasks.append(get_image_text_pair(url=link, img_txt_block=img_txt_block))

            for task in asyncio.as_completed(tasks):
                try:
                    res = await task
                    with open(save_path, "a+", encoding="utf-8") as file:
                        if self.crawl_type == "text":
                            file.write(json.dumps({"content": res, "url": link}, ensure_ascii=False) + "\n")
                        elif self.crawl_type == "img-text":
                            for item in res:
                                file.write(json.dumps(item, ensure_ascii=False) + "\n")
                    if sleep_time:
                        await asyncio.sleep(sleep_time)
                except Exception as e:
                    print(f"Error during task execution: {e}")


if __name__ == "__main__":
    url_path = r"test.json"
    # text = get_content(url=urls_path)

    save_path = r"G:\Musubi\test_res.json"

    crawl = AsyncCrawl(url_path=url_path, crawl_type="text")
    asyncio.run(crawl.crawl_contents(save_path=save_path))
    # crawl.check_content_result()
    # url = "https://www.thenewslens.com/interactive/138105"
    # res = get_content(url)
    # print(res)

    # url = r"https://kmweb.moa.gov.tw/theme_data.php?theme=news&sub_theme=agri_life&id=88958"
    # img_list = get_image_text_pair(url, img_txt_block=["div", "articlepara"])
    # print(img_list)