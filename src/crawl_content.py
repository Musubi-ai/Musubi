import os
from trafilatura import fetch_url, extract
import json
from tqdm import tqdm
import pandas as pd


def get_content(url):
    downloaded = fetch_url(url)
    result = extract(downloaded, favor_precision=True, output_format="markdown")
    return result


class Crawl():
    def __init__(self, urls_path = None):
        self.urls_path = urls_path        

    def check_content_result(self):
        """
        Check the content of the first website in urls_path.
        """
        df = pd.read_json(self.urls_path, lines=True)
        url = df.iloc[0]["link"]
        res = get_content(url=url)
        print(res)

    def crawl_contents(self, 
        start_idx: int = 0, 
        save_path: str = None
        ):
        """
        Crawl all the contents of websites in urls_path.
        """
        save_file = os.path.isfile(save_path)

        # check the file exist or not
        if save_file:
            content_list = pd.read_json(save_path, lines=True)["url"].to_list()
        else:
            content_list = None

        url_df = pd.read_json(self.urls_path, lines=True)
        length = len(url_df)

        for i in tqdm(range(start_idx, length)):
            link = url_df.iloc[i]["link"]
            # skip the content if it is in the file already
            if content_list and link in content_list:
                continue
            result = get_content(url=link)
            dictt = {"content": result, "url": link}

            with open(save_path, "a+", encoding="utf-8") as file:
                file.write(json.dumps(dictt, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    urls_path = f"G:\Crawl4LLM\crawler\台灣經貿網\台灣經貿網新聞_link.json"
    save_path = f"G:\Crawl4LLM\data\中文\台灣經貿網\台灣經貿網新聞.json"

    crawl = Crawl(urls_path=urls_path)
    crawl.crawl_contents(save_path=save_path)
    # crawl.check_content_result()
    # url = "https://www.thenewslens.com/interactive/138105"
    # res = get_content(url)
    # print(res)