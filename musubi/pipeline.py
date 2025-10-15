import asyncio
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import List, Optional
import sys
import os
from loguru import logger
from .crawl_link import Scan, Scroll, OnePage, Click
from .crawl_content import Crawl
from .async_crawl_link import AsyncScan
from .async_crawl_content import AsyncCrawl
from .utils import (
    add_new_website, 
    delete_website_config_by_idx, 
    deduplicate_by_value, 
    get_root_path,
    filter_null_data
)


logger.add(sys.stderr, level="ERROR")


class Pipeline:
    """
    Main class for Musubi service.

    Args:
        website_config_path (`str`):
            websites.json or imgtxt_webs.json.
        log_path (`str`, *optional*):
            path of log file, default to None.
    """
    def __init__(
        self, 
        website_config_path: str = None,
        log_path: Optional[str] = None
    ):
        if not website_config_path:
            config_dir = Path("config")
            config_dir.mkdir(parents=True, exist_ok=True)
            self.website_config_path = Path("config") / "websites.json"
        else:
            self.website_config_path = website_config_path

        if log_path is not None:
            logger.add(log_path, level="INFO", encoding="utf-8", enqueue=True) 

    def start_by_idx(
        self,
        idx: Optional[int],
        start_page: Optional[int] = 0,
        update_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: Optional[str] = None,
    ):
        """
        Crawl articles of website specified by idx in websites.json or imgtxt_webs.json.

        Args:
            idx (`int`, *optional*):
                Which website in websites.json or imgtxt_webs.json to crawl.
            start_page (`int`, *optional*):
                From which page to start crawling urls.
            update_pages (`int`, *optional*):
                How many pages to crawl in update mode. If not None, fuction will switch to update mode and crawl specified number of pages.
                If None, function will switch into add mode and crawl all pages of websites.
            sleep_time (`int`, *optional*):
                Sleep time to prevent ban from website.
            save_dir (`str`, *optional*):
                Folder to save link.json and articles.
        """
        self.args_dict = defaultdict(lambda: None)
        self.website_df = pd.read_json(self.website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        self.website_df_length = len(self.website_df)
        self.is_nan = self.website_df.apply(pd.isna)
        self.name = self.website_df.iloc[idx]["name"]
        if not self.is_nan.iloc[idx]["prefix"]:
            self.args_dict["prefix"] = self.website_df.iloc[idx]["prefix"]
        if not self.is_nan.iloc[idx]["suffix"]:
            self.args_dict["suffix"] = self.website_df.iloc[idx]["suffix"]
        if not self.is_nan.iloc[idx]["root_path"]:
            self.args_dict["root_path"] = self.website_df.iloc[idx]["root_path"]
        self.args_dict["pages"] = self.website_df.iloc[idx]["pages"]
        self.args_dict["page_init_val"] = self.website_df.iloc[idx]["page_init_val"]
        self.args_dict["multiplier"] = self.website_df.iloc[idx]["multiplier"]
        if not self.is_nan.iloc[idx]["block1"]:
            self.args_dict["block1"] = self.website_df.iloc[idx]["block1"]
        if not self.is_nan.iloc[idx]["block2"].all():
            self.args_dict["block2"] = self.website_df.iloc[idx]["block2"]

        self.dir_ = self.website_df.iloc[idx]["dir_"]
        self.class_ = self.website_df.iloc[idx]["class_"]
        if "img_txt_block" in self.website_df.columns:
            self.img_txt_block = self.website_df.iloc[idx]["img_txt_block"]
        else:
            self.img_txt_block = None

        if save_dir is not None:
            self.save_dir = Path(save_dir) / "data" / self.class_ / self.dir_
            self.save_path = Path(self.save_dir) / "{}.json".format(self.name)
        else:
            self.save_dir = Path("data") / self.class_ / self.dir_
            self.save_path = Path(self.save_dir) / "{}.json".format(self.name)

        if os.path.isfile(self.save_path):
            filter_null_data(self.save_path)

        if self.img_txt_block is not None:
            if save_dir is not None:
                self.urls_dir = Path(save_dir) / "imgtxt_crawler" / self.dir_
                url_path = Path(self.urls_dir) / "{}_imgtxt_link.json".format(self.name)
            else:
                self.urls_dir = Path("imgtxt_crawler") / self.dir_
                url_path = Path(self.urls_dir) / "{}_imgtxt_link.json".format(self.name)
        else:
            if save_dir is not None:
                self.urls_dir = Path(save_dir) / "crawler" / self.dir_
                url_path = Path(self.urls_dir) / "{}_link.json".format(self.name)
            else:
                self.urls_dir = Path("crawler") / self.dir_
                url_path = Path(self.urls_dir) / "{}_link.json".format(self.name)
        self.args_dict["url_path"] = url_path
        self.implementation = self.website_df.iloc[idx]["implementation"]
        self.async_ = self.website_df.iloc[idx]["async_"]

        if update_pages:
            self.args_dict["pages"] = self.args_dict["pages"] if self.args_dict["pages"] <= update_pages else update_pages
            indices = self.website_df["idx"].to_list()
            if idx not in indices:
                raise ValueError("In update mode but assigned index does not exist in website.json file.")
        
        urls_folder_path = Path(self.urls_dir)
        urls_folder_path.mkdir(parents=True, exist_ok=True)
        contents_folder_path = Path(self.save_dir)
        contents_folder_path.mkdir(parents=True, exist_ok=True)

        # start scanning the links
        logger.info("Getting urls from {}!".format(self.name))
        if self.implementation not in ["scan", "scroll", "onepage", "click"]:
            raise ValueError("The implementation can only be `scan`, `scroll`, `onepage`, or `click` but got `{}`.".format(self.implementation))
        elif self.implementation == "scan":
            if self.async_:
                scan = AsyncScan(**self.args_dict)
                asyncio.run(scan.crawl_link())
            else:
                scan = Scan(**self.args_dict)
                scan.crawl_link(start_page=start_page)
        elif self.implementation == "scroll":
            scroll = Scroll(**self.args_dict)
            scroll.crawl_link()
        elif self.implementation == "onepage":
            onepage = OnePage(**self.args_dict)
            onepage.crawl_link()
        elif self.implementation == "click":
            click = Click(**self.args_dict)
            click.crawl_link()

        deduplicate_by_value(self.args_dict["url_path"], key="link")
        
        # Start crawling the websites
        logger.info("Crawling contents in urls from {}!".format(self.name))
        if self.img_txt_block is not None:
            crawl = Crawl(self.args_dict["url_path"], crawl_type="img-text")
            crawl.crawl_contents(save_path=self.save_path, sleep_time=sleep_time, img_txt_block=self.img_txt_block)
        else:
            if self.async_:
                crawl = AsyncCrawl(self.args_dict["url_path"], crawl_type="text")
                asyncio.run(crawl.crawl_contents(save_path=self.save_path))
            else:
                crawl = Crawl(self.args_dict["url_path"], crawl_type="text")
                crawl.crawl_contents(save_path=self.save_path, sleep_time=sleep_time, img_txt_block=self.img_txt_block)

    def start_all(
        self,
        start_idx: Optional[int] = 0,
        update_pages: Optional[int] = None,
        save_dir: Optional[str] = None
    ):
        """
        Crawl all websites in website config json file.
        
        Args:
            start_idx (`int`, *optional*):
                From which idx to crawl.
            update_pages (`int`, *optional*):
                How many pages to crawl in update mode. If not None, fuction will switch to update mode and crawl specified number of pages.
                If None, function will switch into add mode and crawl all pages of websites.
            save_dir (`str`, *optional*):
                Folder to save link.json and articles.
        """
        self.website_df = pd.read_json(self.website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        length = len(self.website_df)
        if update_pages:
            logger.info("Start updating pipeline.")
            pages = self.website_df["pages"].to_list()
            pages = [page if page <= update_pages else update_pages for page in pages]
            for i in range(start_idx, length):
                if not self.website_df.iloc[i]["update"]:
                    continue
                try:
                    self.start_by_idx(idx=i, update_pages=pages[i], save_dir=save_dir)
                except KeyboardInterrupt:
                    logger.info("Shutting down program manually.")
                    break
                except Exception:
                    logger.error("Failed to crawl website with idx {} in config {}".format(i, self.website_config_path))
        else:
            for i in range(start_idx, length):
                logger.info("Start crawling pipeline.")
                try:
                    self.start_by_idx(idx=i, save_dir=save_dir)
                except KeyboardInterrupt:
                    logger.info("Shutting down program manually.")
                    break
                except Exception:
                    logger.error("Failed to crawl website with idx {} in config {}".format(i, self.website_config_path))

    def pipeline(
        self,
        idx: Optional[int] = None,
        dir_: Optional[str] = None,
        name: Optional[str] = None,
        class_: Optional[str] = None,
        prefix: str = None,
        suffix: Optional[int] = None,
        root_path: Optional[int] = None,
        pages: int = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        img_txt_block: Optional[List[str]] = None,
        implementation: str = None,
        async_: Optional[bool] = True,
        start_page: Optional[int] = 0,
        sleep_time: Optional[int] = None,
        save_dir: Optional[str] = None,
        update: Optional[bool] = True
    ):
        """
        Add new website into config json file and crawl website.

        Args:
            idx (`int`, *optional*):
                Specify the index of new website in config json file. If none, the index of new
                website will be the next number of max existing index.
            dir_ (`str`, *optional*):
                Folder name of new website.
            name (`str`, *optional*):
                Subfolder name under the website.
            class_ (`str`, *optional*):
                The type of data in the website. The most general case is using the main language
                of the website name, e.g., English, 中文, ...
            prefix (`str`):
                Main prefix of website. The URL Musubi crawling will be formulaized as:
                "prefix1" + str((page_init_val + pages) * multiplier) + "suffix".
            suffix (`str`, *optional*):
                Suffix of the URL if exists.
            root_path (`str`, *optional*):
                Root of the URL if URLs in tags are presented in relative fashion.
            pages (`int`):
                Number of crawling pages.
            page_init_val (`int`, default=1):
                Initial value of page.
            multiplier (`int`, default=1):
                Multiplier of page.
            block1 (`list`):
                List of HTML tag and its class. The first element should be the name of tag,
                e.g., "div" or "article", and the second element should be the class of the tag.
            block2 (`list`, *optional*):
                Second block if crawling nested structure.
            img_txt_block (`list`, *optional*):
                Block for crawling img-text pair on the website.
            implementation (`str`):
                Type of crawling method to crawl URLs on the website. The implementation should
                be one of ``scan``, ``scroll``, ``onepage``, or ``click``, otherwise it will
                raise an error.
            async_ (`bool`, *optional*, default=False):
                If True, crawling website in an asynchronous fashion.
            start_page (int, *optional*, default=0):
                From which page to start crawling URLs. 0 is first page, 1 is second page, etc.
            sleep_time (`int`, *optional*):
                Sleep time to prevent ban from website.
            save_dir (`str`, *optional*):
                Folder to save link.json and articles.
            update (`bool`, *optional*, default=True):
                Update or not during updating mode.

        Example:
            ::

                from musubi import Pipeline

                pipeline = Pipeline()
                config_dict = {
                    "dir_": "test",
                    "name": "test",
                    "class_": "中文",
                    "prefix": "https://www.wazaiii.com/category?tag=17&ntype=&pages=",
                    "suffix": None,
                    "root_path": None,
                    "pages": 5,
                    "page_init_val": 1,
                    "multiplier": 1,
                    "block1": ["div", "entry-image"],
                    "block2": None,
                    "implementation": "scan",
                    "async_": True
                }

                # Start crawling
                pipeline.pipeline(**config_dict)
        """
        new_website_idx = add_new_website(
            idx = idx,
            dir_ = dir_,
            name = name,
            class_ = class_,
            prefix = prefix,
            suffix = suffix,
            root_path = root_path,
            pages = pages,
            block1 = block1,
            block2 = block2,
            img_txt_block = img_txt_block,
            implementation = implementation,
            async_ = async_,
            website_config_path = self.website_config_path,
            page_init_val = page_init_val,
            multiplier = multiplier,
            update=update
        )

        try:
            self.start_by_idx(
                start_page = start_page,
                idx = new_website_idx,
                sleep_time = sleep_time,
                save_dir = save_dir
            )
        except Exception as e:
            logger.error(f"Error : {e}\n, Failed to parse website, delete the idx from webiste config now.")
            delete_website_config_by_idx(idx=new_website_idx, website_config_path=self.website_config_path)