from musubi.pipeline import Pipeline
import argparse


parser = argparse.ArgumentParser()
# arguments for upgrade mode
parser.add_argument("--index", default=130, help="index of website in the website list", type=int)
parser.add_argument("--upgrade-pages", default=50, help="expected pages to scan or scroll in upgrade mode", type=int)
# arguments for config file
parser.add_argument("--websitelist_path", default="config\websites.json", help="webiste config file", type=str)
# arguments for add mode
parser.add_argument("--dir", default="MyApollo", help="webiste name and its corresponding directory", type=str)
parser.add_argument("--name", default="MyApollo文章", help="category of articels in the website", type=str)
parser.add_argument("--class_", default="中文", help="main class of the website", type=str)
parser.add_argument("--prefix", default="https://myapollo.com.tw/blog/page/", help="prefix 1", type=str)
parser.add_argument("--prefix2", default="/", help="prefix 2", type=str)
parser.add_argument("--prefix3", default="https://myapollo.com.tw", help="prefix 3", type=str)
parser.add_argument("--pages", default=46, help="pages of websites", type=int)
parser.add_argument("--block1", default=["h2", "h3"], help="main list of tag and class", type=list)
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


