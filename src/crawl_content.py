import os
import requests
import pymupdf
import pymupdf4llm
import io
import re
from trafilatura import fetch_url, extract
import json
from tqdm import tqdm
import pandas as pd
import time


def formate_pdf(pdf_content: str):
    text_list = pdf_content.split("\n")
    length = len(text_list)

    formated_doc = ""

    for i in range(length):
        line = text_list[i]
        if (len(line) == 0) or (len(line.replace(" ", "")) == 0):
            continue
        if re.search("([一二三四五六七八九十]、\s\w*)|([123456789].\s\w*)|([零壹貳參肆伍陸柒捌玖拾]、\s\w*)|([一二三四五六七八九十]、\w*)|([123456789].\w*)|([零壹貳參肆伍陸柒捌玖拾]、\w*)", line):
            line = "\n" + line + "\n" if i != 0 else line + "\n"
        if line[-1] in ["。", "：", ":", "？", "?", ".", "」", ")", "|", "`", "-", "》"]:
            line = line + "\n"
        if line[0] == "#" and line[-1] != "\n":
            line = line + "\n"
        if len(line) - len(line.lstrip()) == 1:
            line = line.lstrip()
        formated_doc += line

    return formated_doc


def get_content(url):
    if url.endswith(".pdf"):
        request = requests.get(url)
        filestream = io.BytesIO(request.content)
        with pymupdf.open(stream=filestream, filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
        result = formate_pdf(result)
    else:
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
        save_path: str = None,
        sleep_time: int = None
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

            if sleep_time:
                time.sleep(sleep_time)


if __name__ == "__main__":
    urls_path = f"https://ws.ndc.gov.tw/Download.ashx?u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvMC85NDEwL2Y1NjA2NWVhLTg3NTEtNDgwOC04YmYyLTA1YjE0MGVjOTA5My5wZGY%3D&n=6KuW6KGhMTMtNF80LueJueWIpeWgseWwjjAzX%2BaJvuWwi%2BiHuueBo%2BeUoualreacquS%2BhueahOapn%2Bacg%2BKUgOiHuuWMl%2Be%2BjuWci%2BWVhuacg%2BWNiOmkkOacg%2Ba8lOismy5wZGY%3D&icon=..pdf"
    text = get_content(url=urls_path)
    print(text)
    # save_path = f"G:\Musubi\data\中文\超人行銷\超人行銷所有文章.json"

    # crawl = Crawl(urls_path=urls_path)
    # crawl.crawl_contents(save_path=save_path)
    # crawl.check_content_result()
    # url = "https://www.thenewslens.com/interactive/138105"
    # res = get_content(url)
    # print(res)