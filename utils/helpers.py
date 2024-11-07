import json
from typing import List, Optional


def add_new_website(
    idx: int = None,
    dir: str = None,
    name: str = None,
    lang: str = None,
    prefix: str = None,
    prefix2: str = None,
    prefix3: str = None,
    pages: int = None,
    block1: Optional[List] = None,
    block2: Optional[List] = None,
    type: str = None,
    websitelist_path = "websites.json"
):
    if not (idx and dir and name and lang and prefix and pages and block1 and type):
        raise ValueError("Essential information for crawling website is not complete, please check carefully before changing website.json.")
    
    dictt = {
        "idx": idx,
        "dir": dir,
        "name": name,
        "lang": lang,
        "prefix": prefix,
        "prefix2": prefix2,
        "prefix3": prefix3,
        "pages": pages,
        "block1": block1,
        "block2": block2,
        "type": type
    }

    with open(websitelist_path, "a+", encoding="utf-8") as file:
        file.write(json.dumps(dictt, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    add_new_website(
        idx = 25,
        dir = "everylittled",
        name = "最新文章",
        lang = "中文",
        prefix = "https://everylittled.com/articles?page=",
        prefix2 = None,
        prefix3 = None,
        pages = 505,
        block1 = ["div", "list-box"],
        type = "scan"
    )