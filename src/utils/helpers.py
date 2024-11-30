import json
from typing import List, Optional
import warnings
import pandas as pd


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
    exist_idx_list = pd.read_json(websitelist_path, lines=True)["idx"].to_list()
    dir_list = pd.read_json(websitelist_path, lines=True)["dir"].to_list()
    name_list = pd.read_json(websitelist_path, lines=True)["name"].to_list()

    if not idx:
        idx = max(exist_idx_list) + 1

    if idx in exist_idx_list:
        warnings.warn("The index of new website is not assigned or exists alraedy, the index will be automatically assigned to avoid error.")
        idx = max(exist_idx_list) + 1

    if not (idx and dir and name and lang and prefix and pages and block1 and type):
        raise ValueError("Essential information for crawling website is not complete, please check carefully before changing website.json.")
    
    if (dir in dir_list) and (name in name_list):
        warnings.warn("The dir and name of new website exists alraedy.")
    
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

    return idx


def delete_website_by_idx(
    idx: int = None,
    websitelist_path = "websites.json"
):
    """
    Delete website config in website.json by index and sort all configs. 
    """
    website_df = pd.read_json(websitelist_path, lines=True)
    dictts = website_df[website_df["idx"] != idx].to_dict("records")
    length = len(dictts)

    for i in range(length):
        if dictts[i]["idx"] >= idx:
            dictts[i]["idx"] -= 1
        if i == 0:
            with open(websitelist_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(dictts[i], ensure_ascii=False) + "\n")
        else:
            with open(websitelist_path, "a+", encoding="utf-8") as file:
                file.write(json.dumps(dictts[i], ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # add_new_website(
    #     # idx = 25,
    #     dir = "報導者",
    #     name = "教育校園",
    #     lang = "中文",
    #     prefix = "https://www.twreporter.org/categories/education?page=",
    #     prefix2 = None,
    #     prefix3 = "https://www.twreporter.org",
    #     pages = 14,
    #     block1 = ["div", "list-item__Container-sc-1dx5lew-0 kCnicz"],
    #     type = "scan"
    # )

    delete_website_by_idx(idx=147)
