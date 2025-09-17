import os
from bs4 import BeautifulSoup
import pymupdf
import pymupdf4llm
import io
from tqdm import tqdm
from trafilatura import fetch_url, extract
import orjson
import pandas as pd
import aiohttp
import asyncio
from functools import partial
from loguru import logger


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}


async def get_content(url: str = None, session: aiohttp.ClientSession = None):
    if url.endswith(".pdf"):
        async with session.get(url, headers=headers) as request:
            filestream = io.BytesIO(await request.read())
        with pymupdf.open(stream=filestream.getvalue(), filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
    else:
        loop = asyncio.get_event_loop()
        downloaded = await loop.run_in_executor(None, fetch_url, url)
        extract_with_args = partial(extract, filecontent=downloaded, favor_precision=True, output_format="markdown")
        result = await loop.run_in_executor(None, extract_with_args)
    return result, url

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
        url_path: str,
        crawl_type: str = "text",
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
        df = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
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
        save_file = os.path.isfile(save_path)
        content_list = (
            pd.read_json(save_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["url"].to_list()
            if save_file else []
        )

        url_df = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")

        async def worker(coro):
            async with self.semaphore:
                try:
                    res, url = await coro
                    with open(save_path, "ab") as file:
                        if self.crawl_type == "text":
                            file.write(orjson.dumps({"content": res, "url": url}, option=orjson.OPT_NON_STR_KEYS) + b"\n")
                        elif self.crawl_type == "img-text":
                            for item in res:
                                file.write(orjson.dumps(item, option=orjson.OPT_NON_STR_KEYS) + b"\n")

                    if sleep_time is not None:
                        await asyncio.sleep(sleep_time)

                except Exception as e:
                    logger.error(f"Error during task execution: {e}")

        tasks = []
        for i in range(start_idx, len(url_df)):
            link = url_df.iloc[i]["link"]
            if content_list and (link in content_list):
                continue

            if self.crawl_type == "text":
                tasks.append(asyncio.create_task(worker(get_content(url=link))))
            elif self.crawl_type == "img-text":
                tasks.append(asyncio.create_task(worker(get_image_text_pair(url=link, img_txt_block=img_txt_block))))

        if tasks:
            with tqdm(total=len(tasks), desc="Crawling contents") as pbar:
                for task in asyncio.as_completed(tasks):
                    await task
                    pbar.update(1)

        if os.stat(save_path).st_size == 0:
            raise Exception("Saved content file is empty.")


if __name__ == "__main__":
    url_path = r"G:\Musubi\test.json"
    # # text = get_content(url=urls_path)

    save_path = r"G:\Musubi\test_content.json"

    crawl = AsyncCrawl(url_path=url_path, crawl_type="text")
    asyncio.run(crawl.crawl_contents(save_path=save_path))