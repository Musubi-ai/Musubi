import argparse
from ..pipeline import Pipeline


def start_all_command_parser(subparsers=None):
    """Create and configure argument parser for start-all command.

    This function creates an argument parser for the Musubi start-all command,
    which executes the crawling pipeline for all websites defined in the
    configuration file. It supports both initial crawling and update modes.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            start-all-related arguments and defaults set.
    """
    if subparsers is not None:
        parser = subparsers.add_parser("start-all")
    else:
        parser = argparse.ArgumentParser("Musubi start-all command")

    # arguments for config file
    parser.add_argument("--website_config_path", default=None, help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--start_idx", default=0, help="From which idx to crawl.", type=int)
    parser.add_argument("--update_pages", default=None, help="How many pages to crawl in update mode. If not None, fuction will switch to update mode and crawl specified number of pages.", type=int)
    parser.add_argument("--save_dir", default=None, help="Folder to save link.json and articles.", type=str)
    if subparsers is not None:
        parser.set_defaults(func=start_all_command)
    return parser


def start_all_command(args):
    """Execute the start-all command to crawl all configured websites.

    This function runs the pipeline for all websites defined in the
    configuration file. It can operate in either full crawling mode or
    update mode to refresh recent content.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **website_config_path** (str, optional): Path to the website
                configuration file containing all website definitions.
            - **start_idx** (int, optional): Starting index in the configuration
                file from which to begin crawling. Defaults to ``0`` (first website).
            - **update_pages** (int, optional): Number of pages to crawl in update
                mode. If specified, switches to update mode and only crawls the most
                recent pages. If ``None``, performs full crawling.
            - **save_dir** (str, optional): Directory path to save ``link.json`` and
                extracted articles.

    Returns:
        None: This function executes the pipeline and returns nothing.

    Notes:
        - Processes all websites sequentially starting from ``start_idx``.
        - Update mode (when ``update_pages`` is set) only crawls recent pages.
        - Full mode (when ``update_pages`` is ``None``) performs complete crawling.
        - Each website uses its configuration from the config file.
    """
    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.start_all(
        start_idx=args.start_idx,
        update_pages=args.update_pages,
        save_dir=args.save_dir
    )


def start_by_idx_command_parser(subparsers=None):
    """Create and configure argument parser for start-by-idx command.

    This function creates an argument parser for the Musubi start-by-idx command,
    which executes the crawling pipeline for a specific website identified by
    its index in the configuration file. It provides fine-grained control over
    the crawling process for individual websites.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            start-by-idx-related arguments and defaults set.
    """
    if subparsers is not None:
        parser = subparsers.add_parser("start-by-idx")
    else:
        parser = argparse.ArgumentParser("Musubi start-by-idx command")

    # arguments for config file
    parser.add_argument("--website_config_path", default=None, help="webiste config file", type=str)
    # arguments for start_by_idx function
    parser.add_argument("--idx", default=None, help="Which website in websites.json or imgtxt_webs.json to crawl.", type=int)
    parser.add_argument("--start_page", default=None, help="From which page to start crawling urls.", type=int)
    parser.add_argument("--update_pages", default=None, help="How many pages to crawl in update mode. If not None, fuction will switch to update mode and crawl specified number of pages.", type=int)
    parser.add_argument("--sleep_time", default=None, help="Sleep time to prevent ban from website.", type=int)
    parser.add_argument("--save_dir", default=None, help="Folder to save link.json and articles.", type=str)
    if subparsers is not None:
        parser.set_defaults(func=start_by_idx_command)
    return parser


def start_by_idx_command(args):
    """Execute the start-by-idx command to crawl a specific website.

    This function runs the pipeline for a single website identified by its
    index in the configuration file. It provides detailed control over the
    crawling process, including page range, update mode, and timing.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **website_config_path** (str, optional): Path to the website
                configuration file (``websites.json`` or ``imgtxt_webs.json``).
            - **idx** (int, optional): Index of the website in the configuration
                file to crawl.
            - **start_page** (int, optional): Starting page number for crawling
                (0-based index).
            - **update_pages** (int, optional): Number of pages to crawl in update
                mode. If specified, switches to update mode and only crawls the most
                recent pages. If ``None``, performs full crawling.
            - **sleep_time** (int, optional): Delay in seconds between requests to
                prevent being banned by the website.
            - **save_dir** (str, optional): Directory path to save ``link.json``
                and extracted articles.

    Returns:
        None: This function executes the pipeline and returns nothing.

    Notes:

        - Targets a specific website by its index in the config file.
        - Allows precise control over page range and timing.
        - Update mode only crawls recent pages when ``update_pages`` is set.
        - Sleep time helps avoid rate limiting or IP bans.
        - There appears to be a typo in the code: ``args.strat_page`` should be
            ``args.start_page``.
    
    """
    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.start_by_idx(
        idx=args.idx,
        start_page=args.strat_page,
        update_pages=args.update_pages,
        sleep_time=args.sleep_time,
        save_dir=args.save_dir
    )