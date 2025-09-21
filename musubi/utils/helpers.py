import orjson
from typing import List, Optional, Union
from loguru import logger
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from urllib.parse import urlparse
import re


def is_valid_format(
    s: str, 
    prefix: str, 
    suffix: Union[str] = None
):
    """
    Checks if the given string follows the format: prefix + digits + optional suffix.
    
    Args:
        s (str): The string to be checked.
        prefix (str): The required prefix at the beginning of the string.
        suffix (str or None): The optional suffix at the end of the string. If None, no suffix is required.
    
    Returns:
        bool: True if the string matches the format, otherwise False.
    """
    suffix_pattern = re.escape(suffix) if suffix is not None else ""
    pattern = re.compile(rf'^{re.escape(prefix)}\d+{suffix_pattern}$')
    return bool(pattern.match(s))


def add_new_website(
    website_config_path: Optional[str] = None,
    idx: int = None,
    dir: str = None,
    name: str = None,
    class_: str = None,
    prefix: str = None,
    suffix: str = None,
    root_path: str = None,
    pages: int = None,
    block1: list = None,
    block2: Optional[List] = None,
    img_txt_block: Optional[List] = None,
    type: str = None,
    async_: bool = False,
    page_init_val: int = 1,
    multiplier: int = 1,
):
    if not website_config_path:
        website_config_path = Path("config") / "websites.json"
    try:
        exist_idx_list = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["idx"].to_list()
        dir_list = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["dir"].to_list()
        name_list = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["name"].to_list()

        if not idx:
            idx = max(exist_idx_list) + 1

        if idx in exist_idx_list:
            logger.warning("The index of new website is not assigned or exists alraedy, the index will be automatically assigned to avoid error.")
            idx = max(exist_idx_list) + 1
                
        if (dir in dir_list) and (name in name_list):
            logger.warning("The dir and name of new website exists alraedy.")

    except:
        logger.warning("The argument 'website_config_path' is None or json file is empty. Direct to default path and create new config file.")
        default_folder = Path("config")
        default_folder.mkdir(parents=True, exist_ok=True)
        idx = 0

    if not (dir and name and class_ and prefix and pages and block1 and type) and idx is not None:
        raise ValueError("Essential information for crawling website is not complete, please check carefully before changing config json file.")

    if img_txt_block is not None:
        dictt = {
            "idx": idx,
            "dir": dir,
            "name": name,
            "class_": class_,
            "prefix": prefix,
            "suffix": suffix,
            "root_path": root_path,
            "pages": pages,
            "block1": block1,
            "block2": block2,
            "img_txt_block": img_txt_block,
            "type": type
        }
    else:
        dictt = {
            "idx": idx,
            "dir": dir,
            "name": name,
            "class_": class_,
            "prefix": prefix,
            "suffix": suffix,
            "root_path": root_path,
            "pages": pages,
            "block1": block1,
            "block2": block2,
            "type": type,
            "async_": async_,
            "page_init_val": page_init_val,
            "multiplier": multiplier
        }
    with open(website_config_path, "ab") as file:
        file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    return idx


def delete_website_config_by_idx(
    idx: int,
    website_config_path = Path("config") / "websites.json"
):
    """Deletes a website configuration from websites.json by index and reorders remaining configs.

    This function removes a website configuration entry by its index from the JSON file,
    then reindexes all remaining configurations to maintain consecutive ordering.
    If the file becomes empty after deletion, it will be cleared.

    Args:
        idx (int): The index of the website configuration to delete.
        website_config_path (optional): Path to the websites configuration file.
            Defaults to Path("config") / "websites.json".

    Note:
        - The function uses JSONL format (one JSON object per line)
        - After deletion, all configurations with indices >= idx will have their indices decremented by 1
        - If the file becomes empty, it will be cleared rather than containing empty lines

    Examples:
        >>> delete_website_config_by_idx(2)  # Deletes configuration at index 2
        >>> delete_website_config_by_idx(
        ...     idx=1,
        ...     website_config_path=Path("custom/config/websites.json")
        ... )
    """
    website_df = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
    dictts = website_df[website_df["idx"] != idx].to_dict("records")
    length = len(dictts)

    if length == 0:
        # clear file if empty
        with open(website_config_path, "w", encoding="utf-8") as file:
            pass
        return

    for i in range(length):
        if dictts[i]["idx"] >= idx:
            dictts[i]["idx"] -= 1
        mode = "w" if i == 0 else "a"
        with open(website_config_path, mode, encoding="utf-8") as file:
            file.write(
                orjson.dumps(dictts[i], option=orjson.OPT_APPEND_NEWLINE).decode("utf-8")
            )


def recover_correct_url(
    website_config_path: str = None,
    idx: int = None,
    save_dir: Optional[str] = None
):
    config = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow").iloc[idx].to_dict()
    if save_dir is not None:
        urls_dir = Path(save_dir) / "crawler" / config["dir"]
        url_path = Path(urls_dir) / "{}_link.json".format(config["name"])
    else:
        urls_dir = Path("crawler") / config["dir"]
        url_path = Path(urls_dir) / "{}_link.json".format(config["name"])

    if save_dir is not None:
        content_dir = Path(save_dir) / "data" / config["class_"] / config["dir"]
        content_path = Path(save_dir) / "{}.json".format(config["name"])
    else:
        content_dir = Path("data") / config["class_"] / config["dir"]
        content_path = Path(content_dir) / "{}.json".format(config["name"])
    url_df = pd.read_json(url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
    content_df = pd.read_json(content_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")

    assert len(url_df) == len(content_df), "The length of link.json should be the same with that of content.json."

    for i in tqdm(range(len(content_df))):
        content_df.iloc[i]["url"] = url_df.iloc[i]["link"]
    
    content_df.to_json(content_path, orient='records', lines=True, force_ascii=False)


def get_root_path(url: str):
    parse = urlparse(url)
    root_path = parse.scheme + "://" + parse.netloc
    return root_path


if __name__ == "__main__":
    url = "https://www.wsdiscuss.com/category/market-dynamics/world-economy/page/"
    res = get_root_path(url)
    print(res)
