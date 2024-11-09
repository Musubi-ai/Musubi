from src import Crawl, Scan, Scroll
from utils import add_new_website
from typing import List, Optional
import os
import pandas as pd
import argparse


class Pipeline:
    def __init__(
        self, 
        website_path: str = "websites.json",
    ):
        self.website_path = website_path

    def start_by_idx(
        self,
        start_page: int = 0,
        start_idx: int = 0,
        idx: int = None
    ):
        self.website_df = pd.read_json(self.website_path, lines=True)
        self.website_df_length = len(self.website_df)
        self.is_nan = self.website_df.apply(pd.isna)
        self.name = self.website_df.iloc[idx]["name"]
        self.prefix = None if self.is_nan.iloc[idx]["prefix"] else self.website_df.iloc[idx]["prefix"]
        self.prefix2 = None if self.is_nan.iloc[idx]["prefix2"] else self.website_df.iloc[idx]["prefix2"]
        self.prefix3 = None if self.is_nan.iloc[idx]["prefix3"] else self.website_df.iloc[idx]["prefix3"]
        self.pages = self.website_df.iloc[idx]["pages"]
        self.dir = self.website_df.iloc[idx]["dir"]
        self.lang = self.website_df.iloc[idx]["lang"]
        self.block1 = None if self.is_nan.iloc[idx]["block1"] else self.website_df.iloc[idx]["block1"]
        self.block2 = None if self.is_nan.iloc[idx]["block2"].all() else self.website_df.iloc[idx]["block2"]
        self.urls_dir = "crawler\{}".format(self.dir)
        self.save_dir = "data\{}\{}".format(self.lang, self.dir)
        self.urls_path = "crawler\{}\{}_link.json".format(self.dir, self.name)
        self.save_path = "data\{}\{}\{}.json".format(self.lang, self.dir, self.name)
        self.type = self.website_df.iloc[idx]["type"]

        # First check the existence of the directories. If not, build them.
        if not os.path.isdir(self.urls_dir):
            os.makedirs(self.urls_dir)
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        # start scanning the links
        print("---------------------------------------------\nGetting urls from {}!\n---------------------------------------------".format(self.name))
        if self.type == "scan":
            scan = Scan(
                self.prefix,
                self.prefix2,
                self.prefix3,
                self.pages,
                self.block1,
                self.block2,
                self.urls_path
            )
            scan.crawl_link(start_page=start_page)
        elif self.type == "scroll":
            scroll = Scroll(
                self.prefix,
                self.prefix2,
                self.prefix3,
                self.pages,
                self.block1,
                self.block2,
                self.urls_path
            )
            scroll.crawl_link()
        else:
            raise ValueError("The type can only be scan or scroll but got {}.".format(self.type))
        
        # Start crawling the websites
        print("---------------------------------------------\nCrawling contents in urls from {}!\n---------------------------------------------".format(self.name))
        crawl = Crawl(self.urls_path)
        crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx)

    def start_all(self):
        for i in range(self.website_df_length):
            self.start_by_idx(idx=i)

    def pipeline(
        self,
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
        start_page: int = 0,
        start_idx: int = 0,
    ):
        new_website_idx = add_new_website(
            idx = idx,
            dir = dir,
            name = name,
            lang = lang,
            prefix = prefix,
            prefix2 = prefix2,
            prefix3 = prefix3,
            pages = pages,
            block1 = block1,
            block2 = block2,
            type = type,
        )

        self.start_by_idx(
            start_page = start_page,
            start_idx = start_idx,
            idx = new_website_idx
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=33, help="index of website in the website list", type=int)
    parser.add_argument("--dir", default="POPDAILY", help="webiste name and its corresponding directory", type=str)
    parser.add_argument("--name", default="POPDAILY妝漂亮版", help="category of articels in the website", type=str)
    parser.add_argument("--lang", default="中文", help="main language of the website", type=str)
    parser.add_argument("--prefix", default="https://www.popdaily.com.tw/explore/beauty", help="prefix 1", type=str)
    parser.add_argument("--prefix2", default=None, help="prefix 2", type=str)
    parser.add_argument("--prefix3", default=None, help="prefix 3", type=str)
    parser.add_argument("--pages", default=500, help="pages of websites", type=int)
    parser.add_argument("--block1", default=["div", "DesktopGridContainer-sc-1eawaw9-0.cutvQW"], help="main list of tag and class", type=list)
    parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
    parser.add_argument("--type", default="scroll", help="way of crawling websites", type=str)
    args = parser.parse_args()

    pipe = Pipeline()
    pipe.pipeline(
        dir = args.dir,
        name = args.name,
        lang = args.lang,
        prefix = args.prefix,
        prefix2 = args.prefix2,
        prefix3 = args.prefix3,
        pages = args.pages,
        block1 = args.block1,
        block2 = args.block2,
        type =args.type
    )
    # pipe.start_by_idx(idx=args.index)
    # pipe.start_all()