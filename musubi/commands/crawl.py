import argparse
import asyncio
from collections import defaultdict
from ..async_crawl_content import AsyncCrawl
from ..crawl_content import Crawl
from ..crawl_link import Scan, Scroll, OnePage, Click
from ..async_crawl_link import AsyncScan


def crawl_content_command_parser(subparsers=None):
    """Create and configure argument parser for crawl-content command.

    This function creates an argument parser for the Musubi crawl-content command,
    which is used to crawl text content from URLs specified in a JSON file.
    It supports both synchronous and asynchronous crawling modes.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            crawl-content-related arguments and defaults set.
    """
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
    """Execute the crawl-content command to extract text content from URLs.

    This function crawls text content from URLs listed in a JSON file and
    saves the results. It supports both synchronous and asynchronous crawling
    modes based on the ``async_`` flag.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **url_path** (str): Path to the JSON file containing URLs to crawl.
            - **save_path** (str): Path to save the crawled text content as JSON.
            - **start_idx** (int, optional): Starting index for crawling from the
                URL list. Defaults to 0.
            - **sleep_time** (int, optional): Time in seconds to sleep between
                crawling steps.
            - **async_** (bool): Whether to use asynchronous crawling. If ``True``,
                uses ``AsyncCrawl``; if ``False``, uses synchronous ``Crawl``.

    Returns:
        None: This function performs crawling operations and returns nothing.

    Notes:

        - Asynchronous mode uses ``AsyncCrawl`` and ``asyncio.run()``.
        - Synchronous mode uses the standard ``Crawl`` class.
        - There appears to be a typo in the code: ``args.strat_idx`` should be
            ``args.start_idx``.

    """
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
    """Create and configure argument parser for crawl-link command.

    This function creates an argument parser for the Musubi crawl-link command,
    which is used to crawl href links from websites using different strategies
    (scan, scroll, onepage, or click). It supports multiple crawling patterns
    and configurations.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            crawl-link-related arguments and defaults set.
    """
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
    """Execute the crawl-link command to extract links from websites.

    This function crawls href links from websites using one of four strategies:
    ``scan``, ``scroll``, ``onepage``, or ``click``. Each strategy uses a
    different approach to navigate and extract links from web pages.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **type** (str): Crawling strategy to use. Must be one of ``"scan"``, ``"scroll"``, ``"onepage"``, or ``"click"``.
            - **url_path** (str): Path to save the crawled href links as JSON.
            - **prefix** (str): URL prefix for constructing target URLs.
            - **suffix** (str): URL suffix for constructing target URLs.
            - **root_path** (str, optional): Root path of the target website.
            - **pages** (int, optional): Number of pages to crawl.
            - **page_init_val** (int, optional): Initial page number value. Defaults to 1.
            - **multiplier** (int, optional): Multiplier for page number calculation. Defaults to 1.
            - **block1** (list): Main list of HTML tag and class selectors for finding links.
            - **block2** (list, optional): Secondary list of HTML tag and class selectors.
            - **async_** (bool, optional): Whether to use asynchronous crawling (only supported for ``scan`` type). Defaults to ``False``.

    Returns:
        None: This function performs crawling operations and returns nothing.

    Raises:
        ValueError: If the ``type`` argument is not one of the valid choices
            (``scan``, ``scroll``, ``onepage``, ``click``).

    Notes:

        - **Scan**: Supports both synchronous and asynchronous modes.
        - **Scroll**: Crawls pages that load content dynamically when scrolling.
        - **OnePage**: Extracts links from a single page.
        - **Click**: Navigates by clicking elements to discover links.
    
    """
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