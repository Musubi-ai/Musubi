from .crawl_link import Scan, Scroll, OnePage, Click
from .crawl_content import Crawl
from .async_crawl_link import AsyncScan
from .async_crawl_content import AsyncCrawl
from .utils import add_new_website, delete_website_by_idx
import asyncio
from collections import defaultdict
from typing import List, Optional
import warnings
import os
import pandas as pd
import argparse


class Pipeline:
    """
    Main class for Musubi service.

    Args:
        website_path (`str`) config\websites.json or config\imgtxt_webs.json.
    """
    def __init__(
        self, 
        website_path: str = None,
    ):
        self.website_path = website_path

    def start_by_idx(
        self,
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        idx: Optional[int] = None,
        upgrade_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: str = None,
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
            save_dir (`str`):
                Folder to save link.json and articles.
        """
        if idx is None:
            raise ValueError("The index cannot be unassigned, please fill index argument.")
        self.args_dict = defaultdict(lambda: None)
        self.website_df = pd.read_json(self.website_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        self.website_df_length = len(self.website_df)
        self.is_nan = self.website_df.apply(pd.isna)
        self.name = self.website_df.iloc[idx]["name"]
        if not self.is_nan.iloc[idx]["prefix"]:
            self.args_dict["prefix"] = self.website_df.iloc[idx]["prefix"]
        if not self.is_nan.iloc[idx]["prefix2"]:
            self.args_dict["prefix2"] = self.website_df.iloc[idx]["prefix2"]
        if not self.is_nan.iloc[idx]["prefix3"]:
            self.args_dict["prefix3"] = self.website_df.iloc[idx]["prefix3"]
        self.args_dict["pages"] = self.website_df.iloc[idx]["pages"]
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
            self.save_dir = save_dir + "\data\{}\{}".format(self.class_, self.dir)
            self.save_path = save_dir + "\data\{}\{}\{}.json".format(self.class_, self.dir, self.name)
        else:
            self.save_dir = "data\{}\{}".format(self.class_, self.dir)
            self.save_path = "data\{}\{}\{}.json".format(self.class_, self.dir, self.name)

        if self.img_txt_block is not None:
            if save_dir is not None:
                self.urls_dir = save_dir + "\imgtxt_crawler\{}".format(self.dir)
                url_path = save_dir + "\imgtxt_crawler\{}\{}_imgtxt_link.json".format(self.dir, self.name)
            else:
                self.urls_dir = "imgtxt_crawler\{}".format(self.dir)
                url_path = "imgtxt_crawler\{}\{}_imgtxt_link.json".format(self.dir, self.name)
        else:
            if save_dir is not None:
                self.urls_dir = save_dir + "\crawler\{}".format(self.dir)
                url_path = save_dir + "\crawler\{}\{}_link.json".format(self.dir, self.name)
            else:
                self.urls_dir = "crawler\{}".format(self.dir)
                url_path = "crawler\{}\{}_link.json".format(self.dir, self.name)
        self.args_dict["url_path"] = url_path
        self.type = self.website_df.iloc[idx]["type"]
        self.async_ = self.website_df.iloc[idx]["async_"]

        if upgrade_pages:
            print("---------------------------------------------\nIn upgrade mode now, checking whether the index exists or not.\n---------------------------------------------")
            self.args_dict["pages"] = self.args_dict["pages"] if self.args_dict["pages"] <= upgrade_pages else upgrade_pages
            indices = self.website_df["idx"].to_list()
            if idx not in indices:
                raise ValueError("In upgrade mode but assigned index does not exist in website.json file.")
        
        # Check the existence of the directories. If not, build them.
        if not os.path.isdir(self.urls_dir):
            os.makedirs(self.urls_dir)
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        # start scanning the links
        print("---------------------------------------------\nGetting urls from {}!\n---------------------------------------------".format(self.name))
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
        
        # Start crawling the websites
        print("Crawling contents in urls from {}!\n---------------------------------------------".format(self.name))
        if self.img_txt_block is not None:
            crawl = Crawl(self.args_dict["url_path"], crawl_type="img-text")
            print("Crawling image-text pair.")
            crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx, sleep_time=sleep_time, img_txt_block=self.img_txt_block)
        else:
            if self.async_:
                crawl = AsyncCrawl(self.args_dict["url_path"], crawl_type="text")
                asyncio.run(crawl.crawl_contents(save_path=self.save_path))
            else:
                crawl = Crawl(self.args_dict["url_path"], crawl_type="text")
                crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx, sleep_time=sleep_time, img_txt_block=self.img_txt_block)
            print("Crawling pure text data.")
        

    def start_all(
        self,
        start_idx: Optional[int] = 0,
        upgrade_page: Optional[int] = None
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
        self.website_df = pd.read_json(self.website_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")
        length = len(self.website_df)
        if upgrade_page:
            print("---------------------------------------------\nIn upgrade mode now, setting the upgraded page for each website based on upgrade_page argument.\n---------------------------------------------")
            pages = self.website_df["pages"].to_list()
            pages = [page if page <= upgrade_page else upgrade_page for page in pages]
            print("Upgrading text data of each website.\n---------------------------------------------")
            for i in range(start_idx, length):
                self.start_by_idx(idx=i, upgrade_pages=pages[i])
        else:
            print("---------------------------------------------\nIn add mode now.\n---------------------------------------------")
            for i in range(start_idx, length):
                self.start_by_idx(idx=i)

    def pipeline(
        self,
        idx: Optional[int] = None,
        dir: str = None,
        name: str = None,
        class_: str = None,
        prefix: str = None,
        prefix2: Optional[int] = None,
        prefix3: Optional[int] = None,
        pages: int = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        img_txt_block: Optional[List[str]] = None,
        type: str = None,
        async_: bool = False,
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        sleep_time: Optional[int] = None
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
                The type name of data in the website.
            prefix (`str`):
                Main prefix of website. The url Musubi crawling will be formulaized as "prefix1" + str(pages) + "prefix2".
            prefix2 (`str`, *optional*):
                Suffix of the url if exist.
            prefix3 (`str`, *optional*):
                Root of the url if urls in a tags are presented in relative fashion.
            pages (`int`):
                Number of crawling pages.
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
            start_page (`int`, *optional*):
                From which page to start crawling urls.
            start_idx (`int`, ):
                From which idx in link.json to start crawling articles.
            sleep_time (`int`, *optional*):
                Sleep time to prevent ban from website.

        Example:

        ```python
        >>> from musubi import Pipeline

        >>> pipeline = Pipeline("website.json")
        >>> config_dict = {
            "idx": 1, 
            "dir": "法律百科", 
            "name": "法律百科文章", 
            "class_": "中文", 
            "prefix": "https://www.legis-pedia.com/article?page=", 
            "prefix2": None, 
            "prefix3": None, 
            "pages": 106, 
            "block1": ["div", "list-acticle-head tw-mb-2"], 
            "block2": None, 
            "type": "scan",
            "async_": False
            }

        >>> # Start crawling
        >>> pipeline.pipeline(**config_dict)
        """
        new_website_idx = add_new_website(
            idx = idx,
            dir = dir,
            name = name,
            class_ = class_,
            prefix = prefix,
            prefix2 = prefix2,
            prefix3 = prefix3,
            pages = pages,
            block1 = block1,
            block2 = block2,
            img_txt_block = img_txt_block,
            type = type,
            async_ = async_,
            websitelist_path = self.website_path
        )

        try:
            self.start_by_idx(
                start_page = start_page,
                start_idx = start_idx,
                idx = new_website_idx,
                sleep_time = sleep_time
            )
        except:
            warnings.warn("Failed to parse website, delete the idx from webiste config now.")
            delete_website_by_idx(idx=new_website_idx, websitelist_path=self.website_path)


if __name__ == "__main__":
    from tqdm import tqdm
    parser = argparse.ArgumentParser()
    # arguments for upgrade mode
    parser.add_argument("--index", default=130, help="index of website in the website list", type=int)
    parser.add_argument("--upgrade-pages", default=50, help="expected pages to scan or scroll in upgrade mode", type=int)
    # arguments for config file
    parser.add_argument("--websitelist_path", default="config\websites.json", help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--dir", default="test", help="webiste name and its corresponding directory", type=str)
    parser.add_argument("--name", default="test", help="category of articels in the website", type=str)
    parser.add_argument("--class_", default="中文", help="main class of the website", type=str)
    parser.add_argument("--prefix", default="https://www.zhiyin.com.tw/index.php?do=news&p=", help="prefix 1", type=str)
    parser.add_argument("--prefix2", default=None, help="prefix 2", type=str)
    parser.add_argument("--prefix3", default="https://www.zhiyin.com.tw/", help="prefix 3", type=str)
    parser.add_argument("--pages", default=5, help="pages of websites", type=int)
    parser.add_argument("--block1", default=["h2", "blog-title"], help="main list of tag and class", type=list)
    parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
    parser.add_argument("--img_txt_block", default=None, help="main list of tag and class for crawling image-text pair", type=list)
    parser.add_argument("--type", default="scan", help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"])
    args = parser.parse_args()

    pipe = Pipeline(website_path=args.websitelist_path)
    pipe.pipeline(
        dir = args.dir,
        name = args.name,
        class_ = args.class_,
        prefix = args.prefix,
        prefix2 = args.prefix2,
        prefix3 = args.prefix3,
        pages = args.pages,
        block1 = args.block1,
        block2 = args.block2,
        type = args.type,
        img_txt_block = args.img_txt_block,
        sleep_time=None
    )
    # pipe.start_by_idx(
    #         idx=args.index,
    #         # upgrade_pages=50,
    #     )
    # for i in tqdm(range(104, 133)):
    #     pipe.start_by_idx(
    #         idx=i,
    #         upgrade_pages=50,
    #         start_page=258
    #     )
    # pipe.start_all(
    #     upgrade_page=args.upgrade_pages,
    #     start_idx = args.index
    # )