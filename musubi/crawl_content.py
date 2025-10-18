import os
import requests
from bs4 import BeautifulSoup
import pymupdf
import pymupdf4llm
import io
from trafilatura import fetch_url, extract
import orjson
from tqdm import tqdm
import pandas as pd
import time


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}



def get_content(url):
    if url.endswith(".pdf"):
        request = requests.get(url, headers=headers)
        filestream = io.BytesIO(request.content)
        with pymupdf.open(stream=filestream, filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
    else:
        downloaded = fetch_url(url)
        result = extract(downloaded, favor_precision=True, output_format="markdown")
    return result


def get_image_text_pair(
    url: str = None,
    img_txt_block: list = None
):
    request = requests.get(url, headers=headers)
    content = request.text
    soup = BeautifulSoup(content, "html.parser")
    soup = soup.find(img_txt_block[0], class_=img_txt_block[1])
    img_list = []
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        description = img_tag.get("alt")
        img_list.append({"img_url": img_url, "caption": description, "url": url})
    return img_list


class Crawl():
    """A web crawler for extracting text or image-text content from URLs.

    This class provides functionality to crawl websites and extract content based
    on the specified crawl type. It supports both text-only and image-text pair
    extraction modes.

    Args:
        url_path (str): Path to the JSON file containing URLs to crawl.
        crawl_type (str, optional): Type of crawling operation. Should be one of 
            'text' or 'img-text'. Defaults to 'text'.
    """
    def __init__(
        self,
        url_path: str,
        crawl_type: str = "text"
    ):
        self.url_path = url_path
        self.crawl_type = crawl_type     

    def check_content_result(
        self,
        img_txt_block: list = None
    ):
        """Check and print the content of the first website in url_path.

        This method reads the first URL from the url_path file and extracts its
        content based on the crawl_type setting. The result is printed to stdout.

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
            res = get_content(url=url)
        elif self.crawl_type == "img-text":
            res = get_image_text_pair(url=url, img_txt_block=img_txt_block)
        print(res)

    def crawl_contents(
        self, 
        start_idx: int = 0, 
        save_path: str = None,
        sleep_time: int = None,
        img_txt_block: list = None
        ):
        """Crawl and save content from all websites in url_path.

        This method iterates through all URLs in the url_path file, extracts
        content based on the crawl_type, and saves results to a JSONL file.
        It supports resuming from a specific index and skips already crawled URLs.

        Args:
            start_idx (int, optional): Index to start crawling from. Useful for
                resuming interrupted crawls. Defaults to 0.
            save_path (str, optional): Path to save the crawled content as JSONL.
                Defaults to None.
            sleep_time (int, optional): Number of seconds to sleep between requests
                to avoid rate limiting. Defaults to None.
            img_txt_block (list, optional): List of CSS selectors or identifiers
                for image-text blocks. Only used when crawl_type is 'img-text'.
                Defaults to None.

        Returns:
            None: Results are saved to the file specified by save_path.

        Raises:
            Exception: If the saved content file is empty after crawling.

        Note:
            - For 'text' crawl_type, each URL produces one entry with 'content' 
              and 'url' fields.
            - For 'img-text' crawl_type, each URL may produce multiple entries,
              one for each image-text pair found.
        """
        save_file = os.path.isfile(save_path)

        # check the file exist or not
        if save_file:
            content_list = pd.read_json(save_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["url"].to_list()
        else:
            content_list = None

        url_df = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        length = len(url_df)

        
        for i in tqdm(range(start_idx, length), desc="Crawling contents"):
            link = url_df.iloc[i]["link"]
            # skip the content if it is in the file already
            if content_list and (link in content_list):
                continue

            if self.crawl_type == "text":
                result = get_content(url=link)
                dictt = {"content": result, "url": link}
                with open(save_path, "ab") as file:
                    file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")
            elif self.crawl_type == "img-text":
                result = get_image_text_pair(url=link, img_txt_block=img_txt_block)
                for item in result:
                    with open(save_path, "ab") as file:
                        file.write(orjson.dumps(item, option=orjson.OPT_NON_STR_KEYS) + b"\n")

            if sleep_time is not None:
                time.sleep(sleep_time)

        crawl_df = pd.read_json(save_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        if (len(crawl_df) == 0):
            raise Exception("Wrong contents in saved content file.")


if __name__ == "__main__":
    url_path = r"G:\Musubi\test.json"
    # text = get_content(url=url_path)
    # print(text)
    save_path = r"G:\Musubi\test_content.json"

    crawl = Crawl(url_path=url_path, crawl_type="text")
    crawl.crawl_contents(save_path=save_path)
    # crawl.check_content_result()

    # url = "https://www.thenewslens.com/interactive/138105"
    # res = get_content(url)
    # print(res)

    # url = r"https://kmweb.moa.gov.tw/theme_data.php?theme=news&sub_theme=agri_life&id=88958"
    # img_list = get_image_text_pair(url, img_txt_block=["div", "articlepara"])
    # print(img_list)

#     content = """對半導體需求暢旺，進而驅動半導體業者積極投資擴廠，帶動我國半導體設備
# 業產值於109年起突破千億元水準，年增47.3%，之後連續3年呈高速雙位數成
# 長，惟隨全球步入高通膨及高利率環境後，消費及設備投資動能均放緩，112年

# 產值轉年減7.3%，結束自101年以來連續11年成長趨勢，今(113)年隨 AI 商機
# 浪潮崛起，對高效能運算、人工智慧應用之需求強勁，再度加速市場對半導體
# 先進製程之產能需求，推升1-5月產值恢復正成長，年增5.5%。"""
#     res = formate_pdf(content)
#     print(res)