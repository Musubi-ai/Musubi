from .crawl_link import Scan, Scroll, OnePage, Click
from .crawl_content import Crawl
from .async_crawl_link import AsyncScan
from .async_crawl_content import AsyncCrawl
from .utils import add_new_website, delete_website_config_by_idx, deduplicate_by_value
import asyncio
from pathlib import Path
from collections import defaultdict
from typing import List, Optional
import warnings
import pandas as pd
from rich.console import Console


console = Console()


class Pipeline:
    """
    Main class for Musubi service.

    Args:
        website_config_path (`str`) websites.json or imgtxt_webs.json.
    """
    def __init__(
        self, 
        website_config_path: str = None,
    ):
        if not website_config_path:
            config_dir = Path("config")
            config_dir.mkdir(parents=True, exist_ok=True)
            self.website_config_path = Path("config") / "websites.json"
        else:
            self.website_config_path = website_config_path

    def start_by_idx(
        self,
        idx: Optional[int],
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        upgrade_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: Optional[str] = None,
    ):
        """
        Crawl articles of website specified by idx in websites.json or imgtxt_webs.json.

        Args:
            start_page (`int`, *optional*):
                From which page to start crawling urls.
            start_idx (`int`, ):
                From which idx in link.json to start crawling articles.
            idx (`int`, *optional*):
                Which website in websites.json or imgtxt_webs.json to crawl.
            upgrade_pages (`int`, *optional*):
                How many pages to crawl in upgrade mode. If not None, fuction will switch to upgrade mode and crawl specified number of pages.
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

        self.dir = self.website_df.iloc[idx]["dir"]
        self.class_ = self.website_df.iloc[idx]["class_"]
        if "img_txt_block" in self.website_df.columns:
            self.img_txt_block = self.website_df.iloc[idx]["img_txt_block"]
        else:
            self.img_txt_block = None

        if save_dir is not None:
            self.save_dir = Path(save_dir) / "data" / self.class_ / self.dir
            self.save_path = Path(self.save_dir) / "{}.json".format(self.name)
        else:
            self.save_dir = Path("data") / self.class_ / self.dir
            self.save_path = Path(self.save_dir) / "{}.json".format(self.name)

        if self.img_txt_block is not None:
            if save_dir is not None:
                self.urls_dir = Path(save_dir) / "imgtxt_crawler" / self.dir
                url_path = Path(self.urls_dir) / "{}_imgtxt_link.json".format(self.name)
            else:
                self.urls_dir = Path("imgtxt_crawler") / self.dir
                url_path = Path(self.urls_dir) / "{}_imgtxt_link.json".format(self.name)
        else:
            if save_dir is not None:
                self.urls_dir = Path(save_dir) / "crawler" / self.dir
                url_path = Path(self.urls_dir) / "{}_link.json".format(self.name)
            else:
                self.urls_dir = Path("crawler") / self.dir
                url_path = Path(self.urls_dir) / "{}_link.json".format(self.name)
        self.args_dict["url_path"] = url_path
        self.type = self.website_df.iloc[idx]["type"]
        self.async_ = self.website_df.iloc[idx]["async_"]

        if upgrade_pages:
            self.args_dict["pages"] = self.args_dict["pages"] if self.args_dict["pages"] <= upgrade_pages else upgrade_pages
            indices = self.website_df["idx"].to_list()
            if idx not in indices:
                raise ValueError("In upgrade mode but assigned index does not exist in website.json file.")
        
        urls_folder_path = Path(self.urls_dir)
        urls_folder_path.mkdir(parents=True, exist_ok=True)
        contents_folder_path = Path(self.save_dir)
        contents_folder_path.mkdir(parents=True, exist_ok=True)

        # start scanning the links
        console.log("Getting urls from {}!".format(self.name))
        if self.type not in ["scan", "scroll", "onepage", "click"]:
            raise ValueError("The type can only be scan, scroll, onepage, or click but got {}.".format(self.type))
        elif self.type == "scan":
            if self.async_:
                scan = AsyncScan(**self.args_dict)
                asyncio.run(scan.crawl_link())
            else:
                scan = Scan(**self.args_dict)
                scan.crawl_link(start_page=start_page)
        elif self.type == "scroll":
            scroll = Scroll(**self.args_dict)
            scroll.crawl_link()
        elif self.type == "onepage":
            onepage = OnePage(**self.args_dict)
            onepage.crawl_link()
        elif self.type == "click":
            click = Click(**self.args_dict)
            click.crawl_link()

        deduplicate_by_value(self.args_dict["url_path"], key="link")
        
        # Start crawling the websites
        console.log("Crawling contents in urls from {}!".format(self.name))
        if self.img_txt_block is not None:
            crawl = Crawl(self.args_dict["url_path"], crawl_type="img-text")
            crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx, sleep_time=sleep_time, img_txt_block=self.img_txt_block)
        else:
            if self.async_:
                crawl = AsyncCrawl(self.args_dict["url_path"], crawl_type="text")
                asyncio.run(crawl.crawl_contents(save_path=self.save_path))
            else:
                crawl = Crawl(self.args_dict["url_path"], crawl_type="text")
                crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx, sleep_time=sleep_time, img_txt_block=self.img_txt_block)

    def start_all(
        self,
        start_idx: Optional[int] = 0,
        upgrade_pages: Optional[int] = None,
        save_dir: Optional[str] = None
    ):
        """
        Crawl all websites in website config json file.
        
        Args:
            start_idx (`int`, *optional*):
                From which idx to crawl.
            upgrade_pages (`int`, *optional*):
                How many pages to crawl in upgrade mode. If not None, fuction will switch to upgrade mode and crawl specified number of pages.
                If None, function will switch into add mode and crawl all pages of websites.
        """
        self.website_df = pd.read_json(self.website_config_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        length = len(self.website_df)
        if upgrade_pages:
            pages = self.website_df["pages"].to_list()
            pages = [page if page <= upgrade_pages else upgrade_pages for page in pages]
            for i in range(start_idx, length):
                self.start_by_idx(idx=i, upgrade_pages=pages[i], save_dir=save_dir)
        else:
            for i in range(start_idx, length):
                self.start_by_idx(idx=i, save_dir=save_dir)

    def pipeline(
        self,
        idx: Optional[int] = None,
        dir: str = None,
        name: str = None,
        class_: str = None,
        prefix: str = None,
        suffix: Optional[int] = None,
        root_path: Optional[int] = None,
        pages: int = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        img_txt_block: Optional[List[str]] = None,
        type: str = None,
        async_: bool = True,
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        sleep_time: Optional[int] = None,
        save_dir: Optional[str] = None
    ):
        """
        Add new website into config json file and crawl website.

        Args:
            idx (`int`, *optional*):
                Specify the index of new website in config json file. If none, the index of new 
                website will be the next number of max existing index.
            dir (`str`):
                Folder name of new website.
            name (`str`):
                Subfolder name under the website.
            class_ (`str`):
                The type of data in the website. The most general case to use this argument is using the main language of website name, e.g., English, 中文,...
            prefix (`str`):
                Main prefix of website. The url Musubi crawling will be formulaized as "prefix1" + str((page_init_val + pages) * multiplier) + "suffix".
            suffix (`str`, *optional*):
                Suffix of the url if exist.
            root_path (`str`, *optional*):
                Root of the url if urls in tags are presented in relative fashion.
            pages (`int`):
                Number of crawling pages.
            page_init_val (`int`, default=1):
                Initial value of page.
            multiplier (`int`, default=1):
                Multiplier of page.
            block1 (`list`):
                List of html tag and its class. The first element in the list should be the name of tag, e.g., "div" or "article", and the 
                second element in the list should be the class of the tag.
            block2 (`list`, *optional*):
                Second block if crawling nested structure.
            img_txt_block (`list`, *optional*):
                Block for crawling img-text pair on the website.
            type (`str`):
                Type of crawling method to crawl urls on the website. The type should be one of the `scan`, `scroll`, `onepage`, or `click`,
                otherwise it will raise an error.
            async_ (`bool`, , *optional*, default=False):
                If True, crawling website in the asynchronous fashion.
            start_page (`int`, *optional*, default=0):
                From which page to start crawling urls. 0 is first page, 1 is second page, and so forth.
            start_idx (`int`,  default=0):
                From which idx in link.json to start crawling articles.
            sleep_time (`int`, *optional*):
                Sleep time to prevent ban from website.
            save_dir (`str`, *optional*):
                Folder to save link.json and articles.

        Example:

        ```python
        >>> from musubi import Pipeline

        >>> pipeline = Pipeline()
        >>> config_dict = {"dir": "test", 
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
            "type": "scan", 
            "async_": True}

        >>> # Start crawling
        >>> pipeline.pipeline(**config_dict)
        """
        new_website_idx = add_new_website(
            idx = idx,
            dir = dir,
            name = name,
            class_ = class_,
            prefix = prefix,
            suffix = suffix,
            root_path = root_path,
            pages = pages,
            block1 = block1,
            block2 = block2,
            img_txt_block = img_txt_block,
            type = type,
            async_ = async_,
            website_config_path = self.website_config_path,
            page_init_val = page_init_val,
            multiplier = multiplier
        )

        try:
            self.start_by_idx(
                start_page = start_page,
                start_idx = start_idx,
                idx = new_website_idx,
                sleep_time = sleep_time,
                save_dir = save_dir
            )
        except:
            warnings.warn("Failed to parse website, delete the idx from webiste config now.")
            delete_website_config_by_idx(idx=new_website_idx, website_config_path=self.website_config_path)