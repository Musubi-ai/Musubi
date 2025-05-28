import argparse
from ..async_crawl_content import AsyncCrawl
from ..crawl_content import Crawl


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
        ...
    else:
        ...
        