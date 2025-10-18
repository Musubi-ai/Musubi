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


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


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
    """An asynchronous web crawler for extracting text or image-text content from URLs.

    This class provides asynchronous functionality to crawl websites and extract 
    content based on the specified crawl type. It supports concurrent crawling with
    configurable task limits to avoid overwhelming the server or hitting rate limits.

    Args:
        url_path (str): Path to the JSON file containing URLs to crawl.
        crawl_type (str, optional): Type of crawling operation. Should be one of 
            'text' or 'img-text'. Defaults to 'text'.
        max_concurrent_tasks (int, optional): Maximum number of concurrent crawling
            tasks allowed. Defaults to 30.
    """
    def __init__(
        self,
        url_path: str,
        crawl_type: str = "text",
        max_concurrent_tasks: int = 30,
    ):
        self.url_path = url_path
        self.crawl_type = crawl_type     
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def check_content_result(
        self,
        img_txt_block: list = None
    ):
        """Check and print the content of the first website in url_path asynchronously.

        This method reads the first URL from the url_path file and extracts its
        content based on the crawl_type setting. The result is printed to stdout.
        This is an asynchronous operation.

        Args:
            img_txt_block (list, optional): List of CSS selectors or identifiers 
                for image-text blocks. Only used when crawl_type is 'img-text'. 
                Defaults to None.

        Returns:
            None: Prints the extracted content to stdout.
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
        """Crawl and save content from all websites in url_path asynchronously.

        This method concurrently crawls all URLs in the url_path file, extracts
        content based on the crawl_type, and saves results to a JSONL file. It uses
        a semaphore to limit concurrent tasks and supports resuming from a specific
        index. Already crawled URLs are automatically skipped.

        Args:
            start_idx (int, optional): Index to start crawling from. Useful for
                resuming interrupted crawls. Defaults to 0.
            save_path (str, optional): Path to save the crawled content as JSONL.
                Defaults to None.
            sleep_time (int, optional): Number of seconds to sleep between completed
                requests to avoid rate limiting. Defaults to None.
            img_txt_block (list, optional): List of CSS selectors or identifiers
                for image-text blocks. Only used when crawl_type is 'img-text'.
                Defaults to None.

        Returns:
            None: Results are saved to the file specified by save_path.

        Raises:
            Exception: If the saved content file is empty after crawling.

        Note:
            - Concurrent tasks are limited by the max_concurrent_tasks parameter
              set during initialization.
            - For 'text' crawl_type, each URL produces one entry with 'content' 
              and 'url' fields.
            - For 'img-text' crawl_type, each URL may produce multiple entries,
              one for each image-text pair found.
            - Errors during individual task execution are logged but do not stop
              the overall crawling process.
            - A progress bar is displayed showing the number of completed tasks.
        """
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