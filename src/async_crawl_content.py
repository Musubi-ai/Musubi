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


async def get_content(
    url: str = None, 
    session: aiohttp.ClientSession = None
):
    if url.endswith(".pdf"):
        async with session.get(url, headers=headers) as request:
            filestream = await io.BytesIO(request.content)
        with pymupdf.open(stream=filestream, filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
        result = formate_pdf(result)
    else:
        downloaded = await fetch_url(url)
        result = extract(downloaded, favor_precision=True, output_format="markdown")
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


class Crawl():
    """
    Args:
        crawl_type (`str`) should be one of 'text' or 'img-text' 
    """
    def __init__(
        self,
        urls_path: str = None,
        crawl_type: str = None,
        max_concurrent_tasks: int = 5,
    ):
        self.urls_path = urls_path
        self.crawl_type = crawl_type     
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def check_content_result(
        self,
        img_txt_block: list = None
    ):
        """
        Check the content of the first website in urls_path.
        """
        df = pd.read_json(self.urls_path, lines=True)
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
        """
        Crawl all the contents of websites in urls_path.
        """
        async with self.semaphore:
            save_file = os.path.isfile(save_path)

            # check the file exist or not
            if save_file:
                content_list = pd.read_json(save_path, lines=True)["url"].to_list()
            else:
                content_list = None

            url_df = pd.read_json(self.urls_path, lines=True)
            length = len(url_df)

            tasks = []

            for i in tqdm(range(start_idx, length)):
                link = url_df.iloc[i]["link"]
                # skip the content if it is in the file already
                if content_list and link in content_list:
                    continue

                if self.crawl_type == "text":
                    tasks.append(get_content(url=link))
                elif self.crawl_type == "img-text":
                    tasks.append(get_image_text_pair(url=link, img_txt_block=img_txt_block))
            
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                res = await task
                if self.crawl_type == "text":
                    result = extract(res, favor_precision=True, output_format="markdown")
                    dictt = {"content": result, "url": link}
                    with open(save_path, "a+", encoding="utf-8") as file:
                        file.write(json.dumps(dictt, ensure_ascii=False) + "\n")
                elif self.crawl_type == "img-text":
                    for item in result:
                        with open(save_path, "a+", encoding="utf-8") as file:
                            file.write(json.dumps(item, ensure_ascii=False) + "\n")

                if sleep_time:
                    time.sleep(sleep_time)


if __name__ == "__main__":
    urls_path = r"C:\Python\Crawl4LLM\test.json"
    # text = get_content(url=urls_path)

    save_path = r"C:\Python\Crawl4LLM\test_res.json"

    crawl = Crawl(urls_path=urls_path, crawl_type="text")
    asyncio.run(crawl.crawl_contents(save_path=save_path))
    # crawl.check_content_result()
    # url = "https://www.thenewslens.com/interactive/138105"
    # res = get_content(url)
    # print(res)

    # url = r"https://kmweb.moa.gov.tw/theme_data.php?theme=news&sub_theme=agri_life&id=88958"
    # img_list = get_image_text_pair(url, img_txt_block=["div", "articlepara"])
    # print(img_list)