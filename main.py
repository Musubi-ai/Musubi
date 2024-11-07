from utils import Crawl, Scan
import os
import pandas as pd
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("--index", default=24, help="index of website in the website list", type=int)

args = parser.parse_args()


class Pipeline:
    def __init__(
        self, 
        website_list: str = "websites.json",
    ):
        self.website_list = pd.read_json(website_list, lines=True)
        self.website_list_length = len(self.website_list)
        self.is_nan = self.website_list.apply(pd.isna)

    def start(
        self, 
        start_page: int = 0,
        start_idx: int = 0,
        idx: int = args.index
    ):
        self.name = self.website_list.iloc[idx]["name"]
        self.prefix = None if self.is_nan.iloc[idx]["prefix"] else self.website_list.iloc[idx]["prefix"]
        self.prefix2 = None if self.is_nan.iloc[idx]["prefix2"] else self.website_list.iloc[idx]["prefix2"]
        self.prefix3 = None if self.is_nan.iloc[idx]["prefix3"] else self.website_list.iloc[idx]["prefix3"]
        self.pages = self.website_list.iloc[idx]["pages"]
        self.dir = self.website_list.iloc[idx]["dir"]
        self.lang = self.website_list.iloc[idx]["lang"]
        self.block1 = None if self.is_nan.iloc[idx]["block1"] else self.website_list.iloc[idx]["block1"]
        self.block2 = None if self.is_nan.iloc[idx]["block2"].all() else self.website_list.iloc[idx]["block2"]
        self.urls_dir = "crawler\{}".format(self.dir)
        self.save_dir = "data\{}\{}".format(self.lang, self.dir)
        self.urls_path = "crawler\{}\{}_link.json".format(self.dir, self.name)
        self.save_path = "data\{}\{}\{}.json".format(self.lang, self.dir, self.name)
        self.type = self.website_list.iloc[idx]["type"]

        # First check the existence of the directories. If not, build them.
        if not os.path.isdir(self.urls_dir):
            os.makedirs(self.urls_dir)
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        # start scanning the links
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

        # TODO: add scroll implementation
        elif self.type == "scroll":
            pass
        else:
            raise ValueError("The type can only be scan or scroll but got {}.".format(self.type))
        
        # Start getting the urls
        print("---------------------------------------------\nstart getting the urls from {}!\n---------------------------------------------".format(self.name))
        scan.crawl_link(start_page=start_page)

        # Start crawling the websites
        print("---------------------------------------------\nstart crawling the contents in urls from {}!\n---------------------------------------------".format(self.name))
        crawl = Crawl(self.urls_path)
        crawl.crawl_contents(save_path=self.save_path, start_idx=start_idx)

    def start_all(self):
        for i in range(self.website_list_length):
            self.start(idx=i)


if __name__ == "__main__":
    pipe = Pipeline()
    # pipe.start()
    # pipe.start_all()