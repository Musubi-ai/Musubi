import os
import requests
from bs4 import BeautifulSoup
import pymupdf
import pymupdf4llm
import io
import re
from trafilatura import fetch_url, extract
import json
from rich.progress import SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, Progress, MofNCompleteColumn, TimeElapsedColumn
import pandas as pd
import time


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


def formate_pdf(pdf_content: str):
    text_list = pdf_content.split("\n")
    length = len(text_list)

    formated_doc = ""

    for i in range(length):
        line = text_list[i]
        if (len(line) == 0) or (len(line.replace(" ", "")) == 0):
            continue
        if re.search(r"([一二三四五六七八九十]、\s\w*)|([123456789].\s\w*)|([零壹貳參肆伍陸柒捌玖拾]、\s\w*)|([一二三四五六七八九十]、\w*)|([零壹貳參肆伍陸柒捌玖拾]、\w*)", line):
            line = "\n" + line + "\n" if i != 0 else line + "\n"
        if line[-1] in ["。", "：", ":", "？", "?", ".", "」", ")", "|", "`", "-", "》"]:
            line = line + "\n"
        if line[0] == "#" and line[-1] != "\n":
            line = line + "\n"
        if len(line) - len(line.lstrip()) > 0:
            line = line.lstrip()
        formated_doc += line

    return formated_doc


def get_content(url):
    if url.endswith(".pdf"):
        request = requests.get(url, headers=headers)
        filestream = io.BytesIO(request.content)
        with pymupdf.open(stream=filestream, filetype="pdf") as doc:
            result = pymupdf4llm.to_markdown(doc)
        result = formate_pdf(result)
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
    """
    Args:
        crawl_type (`str`) should be one of 'text' or 'img-text' 
    """
    def __init__(
        self,
        url_path: str = None,
        crawl_type: str = None
    ):
        self.url_path = url_path
        self.crawl_type = crawl_type     

    def check_content_result(
        self,
        img_txt_block: list = None
    ):
        """
        Check the content of the first website in url_path.
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
        """
        Crawl all the contents of websites in url_path.
        """
        save_file = os.path.isfile(save_path)

        # check the file exist or not
        if save_file:
            content_list = pd.read_json(save_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["url"].to_list()
        else:
            content_list = None

        url_df = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        length = len(url_df)

        with progress:
            for i in progress.track(range(start_idx, length), description="[bright_cyan]Crawl contents"):
                link = url_df.iloc[i]["link"]
                # skip the content if it is in the file already
                if content_list and (link in content_list):
                    continue

                if self.crawl_type == "text":
                    result = get_content(url=link)
                    dictt = {"content": result, "url": link}
                    with open(save_path, "a+", encoding="utf-8") as file:
                        file.write(json.dumps(dictt, ensure_ascii=False) + "\n")
                elif self.crawl_type == "img-text":
                    result = get_image_text_pair(url=link, img_txt_block=img_txt_block)
                    for item in result:
                        with open(save_path, "a+", encoding="utf-8") as file:
                            file.write(json.dumps(item, ensure_ascii=False) + "\n")

                if sleep_time:
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