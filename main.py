from musubi.pipeline import Pipeline
import argparse
from musubi.utils.helpers import delete_website_by_idx
from musubi.utils.deduplicate import deduplicate_by_value
from musubi.utils.helpers import recover_correct_url
from tqdm import tqdm
import glob


parser = argparse.ArgumentParser()
# arguments for upgrade mode
parser.add_argument("--index", default=130, help="index of website in the website list", type=int)
parser.add_argument("--upgrade_pages", default=50, help="expected pages to scan or scroll in upgrade mode", type=int)
# arguments for config file
parser.add_argument("--websitelist_path", default="config\websites.json", help="webiste config file", type=str)
# arguments for add mode
parser.add_argument("--dir", default="test", help="webiste name and its corresponding directory", type=str)
parser.add_argument("--name", default="test-all", help="category of articels in the website", type=str)
parser.add_argument("--class_", default="中文", help="main class of the website", type=str)
parser.add_argument("--prefix", default="https://www.onejapan.com.tw/blog/all?pgno=", help="prefix of url", type=str)
parser.add_argument("--suffix", default=None, help="suffix of url", type=str)
parser.add_argument("--root_path", default=None, help="root path of root website", type=str)
parser.add_argument("--pages", default=5, help="pages of websites", type=int)
parser.add_argument("--block1", default=["div", "card mb-3 custom-hover"], help="main list of tag and class", type=list)
parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
parser.add_argument("--img_txt_block", default=None, help="main list of tag and class for crawling image-text pair", type=list)
parser.add_argument("--type", default="scan", help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"])
parser.add_argument("--async_", default=True, help="asynchronous crawling or not", type=bool)
args = parser.parse_args()


pipe = Pipeline(website_path=args.websitelist_path)

pipe.pipeline(
    dir = args.dir,
    name = args.name,
    class_ = args.class_,
    prefix = args.prefix,
    suffix = args.suffix,
    root_path = args.root_path,
    pages = args.pages,
    block1 = args.block1,
    block2 = args.block2,
    type = args.type,
    img_txt_block = args.img_txt_block,
    async_ = args.async_,
    sleep_time=None
    )

# pipe.start_by_idx(idx=2, upgrade_pages=1)

# for i in tqdm(range(231, 247)):
#     pipe.start_by_idx(idx=i)

# pipe.start_all(
#     start_idx=221,
#     upgrade_pages=args.upgrade_pages
# )

# delete_website_by_idx(idx = 227, websitelist_path=args.websitelist_path)


# files = glob.glob("G:\Musubi\data\中文\芋傳媒\*.json")

# for file in files:
#     deduplicate_by_value(file, key="url")

# recover_correct_url(idx=246)