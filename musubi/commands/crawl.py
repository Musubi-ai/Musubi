import argparse
import asyncio
from collections import defaultdict
from ..async_crawl_content import AsyncCrawl
from ..crawl_content import Crawl
from ..crawl_link import Scan, Scroll, OnePage, Click
from ..async_crawl_link import AsyncScan


def crawl_content_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("crawl-content")
    else:
        parser = argparse.ArgumentParser("Musubi crawl-content command")
    parser.add_argument(
        "--url_path", type=str, default=None, help="Path of json file to save crawled text content.", required=True
    )
    parser.add_argument(
        "--save_path", type=str, default=None, help="Path of json file to save crawled text content.", required=True
    )
    parser.add_argument(
        "--start_idx", type=int, default=0, help="Start index of row in crawl_link json file"
    )
    parser.add_argument(
        "--sleep_time", type=int, default=None, help="Sleep time between each crawling steps."
    )
    parser.add_argument(
        "--async_", type=bool, default=False, help="Crawling web text content in asynchronous way or not.", required=True
    )
    if subparsers is not None:
        parser.set_defaults(func=crawl_content_command)
    return parser


def crawl_content_command(args):
    if args.async_ == True:
        crawl = AsyncCrawl(url_path=args.url_path)
        asyncio.run(crawl.crawl_contents(
            start_idx=args.strat_idx,
            save_path=args.save_path,
            sleep_time=args.sleep_time
        ))
    else:
        crawl = Crawl(url_path=args.url_path)
        crawl.crawl_contents(
            start_idx=args.strat_idx,
            save_path=args.save_path,
            sleep_time=args.sleep_time,
        )

    
def crawl_link_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("crawl-link")
    else:
        parser = argparse.ArgumentParser("Musubi crawl-link command")
    parser.add_argument("--type", default="scan", help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"], required=True)
    parser.add_argument("--url_path", type=str, default=None, help="Path of json file to save crawled href links.", required=True)
    parser.add_argument("--prefix", default=None, help="prefix of url", type=str, required=True)
    parser.add_argument("--suffix", default=None, help="suffix of url", type=str, required=True)
    parser.add_argument("--root_path", default=None, help="root path of root website", type=str)
    parser.add_argument("--pages", default=None, help="pages of websites", type=int)
    parser.add_argument("--page_init_val", default=1, help="Initial value of pages", type=int)
    parser.add_argument("--multiplier", default=1, help="Multiplier of pages", type=int)
    parser.add_argument("--block1", default=None, help="main list of tag and class", type=list, required=True)
    parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
    parser.add_argument("--async_", default=False, help="asynchronous crawling or not", type=bool)
    
    if subparsers is not None:
        parser.set_defaults(func=crawl_link_command)
    return parser


def crawl_link_command(args):
    args_dict = defaultdict(lambda: None)
    args_dict["prefix"] = args.prefix
    args_dict["suffix"] = args.suffix
    args_dict["root_path"] = args.root_path
    args_dict["pages"] = args.pages
    args_dict["page_init_val"] = args.page_init_val
    args_dict["multiplier"] = args.multiplier
    args_dict["block1"] = args.block1
    args_dict["block2"] = args.block2
    args_dict["url_path"] = args.url_path
    
    if args.type not in ["scan", "scroll", "onepage", "click"]:
        raise ValueError("The type can only be scan, scroll, onepage, or click but got {}.".format(args.type))
    elif args.type == "scan":
        if args.async_:
            scan = AsyncScan(**args_dict)
            asyncio.run(scan.crawl_link())
        else:
            scan = Scan(**args_dict)
            scan.crawl_link()
    elif args.type == "scroll":
        scroll = Scroll(**args_dict)
        scroll.crawl_link()
    elif args.type == "onepage":
        onepage = OnePage(**args_dict)
        onepage.crawl_link()
    elif args.type == "click":
        click = Click(**args_dict)
        click.crawl_link()