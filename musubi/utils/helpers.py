import orjson
from typing import List, Optional, Union
from loguru import logger
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup


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


def split_title(title: str):
    separators = r"[-|:]"
    parts = re.split(separators, title)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def add_new_website(
    website_config_path: Optional[str] = None,
    idx: int = None,
    dir_: Optional[str] = None,
    name: Optional[str] = None,
    class_: Optional[str] = None, 
    prefix: str = None,
    suffix: str = None,
    root_path: Optional[str] = None,
    pages: int = None,
    block1: list = None,
    block2: Optional[List] = None,
    img_txt_block: Optional[List] = None,
    implementation: str = None,
    async_: bool = False,
    page_init_val: int = 1,
    multiplier: int = 1,
    update: Optional[bool] = True
):
    """Add a new website configuration to the website configuration file.

    This function creates a new website entry with the specified crawling parameters
    and appends it to the configuration file in JSONL format. It automatically
    handles index assignment, duplicate detection, and optional automatic naming
    by parsing the website's title.

    Args:
        website_config_path (str, optional): Path to the website configuration JSON
            file. If None, defaults to 'config/websites.json'. Defaults to None.
        idx (int, optional): Unique identifier for the website. If None or already
            exists, automatically assigns the next available index. Defaults to None.
        dir_ (str, optional): Main directory name for the website. If None, attempts
            to extract from the website's title. Defaults to None.
        name (str, optional): Full name identifier for the website. If None, attempts
            to generate from the website's title. Defaults to None.
        class_ (str, optional): Classification or category for the website. If None,
            defaults to 'Musubi_data'. Defaults to None.
        prefix (str): Base URL or prefix for generating page URLs. Required parameter.
        suffix (str, optional): Suffix to append after page numbers in URLs.
            Defaults to None.
        root_path (str, optional): Root domain path for constructing absolute URLs
            from relative links. Defaults to None.
        pages (int): Number of pages to crawl or scroll/click times. Required parameter.
        block1 (list): List containing [tag_name, class_name] for the primary HTML
            block selector. Required parameter.
        block2 (list, optional): List containing [tag_name, class_name] for a nested
            HTML block selector or clickable button. Defaults to None.
        img_txt_block (list, optional): List of selectors for extracting image-text
            pairs. If provided, only this and common parameters are saved.
            Defaults to None.
        implementation (str): Crawler type to use. Must be one of 'scan', 'scroll',
            'onepage', or 'click'. Required parameter.
        async_ (bool, optional): Whether to use asynchronous crawling. Only saved
            when img_txt_block is None. Defaults to False.
        page_init_val (int, optional): Initial value for page numbering. Only saved
            when img_txt_block is None. Defaults to 1.
        multiplier (int, optional): Multiplier for page numbers in URL generation.
            Only saved when img_txt_block is None. Defaults to 1.
        update (bool, optional): Flag indicating whether this configuration should
            be updated. Defaults to True.

    Returns:
        int: The index (idx) assigned to the newly added website configuration.

    Note:
        - The function automatically creates the config directory if it doesn't exist.
        - If idx already exists or is None, a new unique index is automatically assigned.
        - If `dir_` and `name` are not provided, the function attempts to extract them
          by parsing the website's <title> tag.
        - For 'scan' implementation, uses the second page URL for title parsing.
        - The configuration is saved in JSONL format with one entry per line.
        - Two different configuration formats are used depending on whether
          img_txt_block is provided.
    """
    if not website_config_path:
        website_config_path = Path("config") / "websites.json"

    try:
        df = pd.read_json(website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        exist_idx_list = df["idx"].to_list()
        dir_list = df["dir_"].to_list()
        name_list = df["name"].to_list()

        if not idx:
            idx = max(exist_idx_list) + 1

        if idx in exist_idx_list:
            logger.warning("The index of new website is not assigned or exists alraedy, the index will be automatically assigned to avoid error.")
            idx = max(exist_idx_list) + 1
                
        if (dir_ in dir_list) and (name in name_list):
            logger.warning("The dir_ and name of new website exists alraedy.")
    except Exception:
        logger.warning("The argument 'website_config_path' is None or json file is empty. Direct to default path and create new config file.")
        default_folder = Path("config")
        default_folder.mkdir(parents=True, exist_ok=True)
        idx = 0

    if not (prefix and pages and block1 and implementation) and idx is not None:
        raise ValueError("Essential information for crawling website is not complete, please check carefully before changing config json file.")
    
    if dir_ is None or name is None:
        if implementation in ["onepage", "click", "scroll"]:
            try:
                response = requests.get(prefix)
                soup = BeautifulSoup(response.text, "html.parser")
                title_text = soup.title.string
            except Exception:
                logger.error("Failed to parse title. Please input 'dir_' and 'name' arguments.")
                raise ValueError()
        elif implementation == "scan":
            if suffix is not None:
                url = prefix + str((page_init_val + 1) * multiplier) + suffix
            else:
                url = prefix + str((page_init_val + 1) * multiplier)
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                title_text = soup.title.string
            except Exception:
                logger.error("Failed to parse title. Please input 'dir_' and 'name' arguments.")
                raise ValueError()
        
        if title_text:
            splitted_title = split_title(title_text)

            if len(splitted_title) > 1:
                dir_ = splitted_title[-1]
                name = splitted_title[-1] + "-" + splitted_title[0]
            elif len(splitted_title) == 1:
                dir_ = splitted_title[0]
                name = splitted_title[0]

    if class_ is None:
        class_ = "Musubi_data" # Crawl with Musubi!

    if img_txt_block is not None:
        dictt = {
            "idx": idx,
            "dir_": dir_,
            "name": name,
            "class_": class_,
            "prefix": prefix,
            "suffix": suffix,
            "root_path": root_path,
            "pages": pages,
            "block1": block1,
            "block2": block2,
            "img_txt_block": img_txt_block,
            "implementation": implementation,
            "update": update
        }
    else:
        dictt = {
            "idx": idx,
            "dir_": dir_,
            "name": name,
            "class_": class_,
            "prefix": prefix,
            "suffix": suffix,
            "root_path": root_path,
            "pages": pages,
            "block1": block1,
            "block2": block2,
            "implementation": implementation,
            "async_": async_,
            "page_init_val": page_init_val,
            "multiplier": multiplier,
            "update": update
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
        ::
            delete_website_config_by_idx(2)  # Deletes configuration at index 2
            delete_website_config_by_idx(
            idx=1,
            website_config_path=Path("custom/config/websites.json")
            )
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
        urls_dir = Path(save_dir) / "crawler" / config["dir_"]
        url_path = Path(urls_dir) / "{}_link.json".format(config["name"])
    else:
        urls_dir = Path("crawler") / config["dir_"]
        url_path = Path(urls_dir) / "{}_link.json".format(config["name"])

    if save_dir is not None:
        content_dir = Path(save_dir) / "data" / config["class_"] / config["dir_"]
        content_path = Path(save_dir) / "{}.json".format(config["name"])
    else:
        content_dir = Path("data") / config["class_"] / config["dir_"]
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
