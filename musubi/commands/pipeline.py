import argparse
from ..pipeline import Pipeline


def pipeline_command_parser(subparsers=None):
    """Create and configure argument parser for pipeline command.

    This function creates an argument parser for the Musubi pipeline command,
    which orchestrates the complete web crawling and content extraction workflow.
    It configures website-specific parameters, crawling strategies, and output
    settings for the automated pipeline process.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            pipeline-related arguments and defaults set.

    Note:
        The parser includes three categories of arguments:
        - Configuration: website_config_path for loading existing configs
        - Website structure: URL patterns, page navigation, and HTML selectors
        - Execution control: crawling mode, async settings, and update behavior
    """
    if subparsers is not None:
        parser = subparsers.add_parser("pipeline")
    else:
        parser = argparse.ArgumentParser("Musubi pipeline command")

    # arguments for config file
    parser.add_argument("--website_config_path", default=None, help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--dir_", default=None, help="webiste name and its corresponding directory", type=str, required=True)
    parser.add_argument("--name", default=None, help="category of articels in the website", type=str, required=True)
    parser.add_argument("--class_", default=None, help="main class of the website", type=str, required=True)
    parser.add_argument("--prefix", default=None, help="prefix of url", type=str, required=True)
    parser.add_argument("--suffix", default=None, help="suffix of url", type=str)
    parser.add_argument("--root_path", default=None, help="root path of root website", type=str)
    parser.add_argument("--pages", default=None, help="pages of websites", type=int, required=True)
    parser.add_argument("--page_init_val", default=1, help="Initial value of pages", type=int)
    parser.add_argument("--multiplier", default=1, help="Multiplier of pages", type=int)
    parser.add_argument("--block1", default=None, help="main list of tag and class", type=list, required=True)
    parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
    parser.add_argument("--img_txt_block", default=None, help="main list of tag and class for crawling image-text pair", type=list)
    parser.add_argument("--implementation", default=None, help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"], required=True)
    parser.add_argument("--async_", default=True, help="asynchronous crawling or not", type=bool, required=True)
    parser.add_argument("--start_page", default=1, help="From which page to start crawling urls. 0 is first page, 1 is second page, and so forth.", type=int)
    parser.add_argument("--sleep_time", default=1, help="Sleep time to prevent ban from website.", type=int)
    parser.add_argument("--save_dir", default=None, help="Folder to save link.json and articles.", type=str)
    parser.add_argument("--update", default=True, help="Update or not during updating mode.", type=bool)
    if subparsers is not None:
        parser.set_defaults(func=pipeline_command)
    return parser


def pipeline_command(args):
    """Execute the pipeline command for automated web crawling and content extraction.

    This function runs the complete Musubi pipeline workflow, which includes
    crawling links from websites, extracting content, and saving the results.
    It supports various crawling strategies and can operate in both initial
    collection and update modes.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **website_config_path** (str, optional): Path to the existing website
                configuration file.
            - **dir_** (str): Website name and its corresponding output directory.
            - **name** (str): Category or name identifier for articles on the website.
            - **class_** (str): Main classification of the website.
            - **prefix** (str): URL prefix for constructing target URLs.
            - **suffix** (str, optional): URL suffix for constructing target URLs.
            - **root_path** (str, optional): Root path of the target website.
            - **pages** (int): Total number of pages to crawl.
            - **page_init_val** (int, optional): Initial page number value.
                Defaults to 1.
            - **multiplier** (int, optional): Multiplier for page number
                calculation. Defaults to 1.
            - **block1** (list): Main list of HTML tag and class selectors for
                link extraction.
            - **block2** (list, optional): Secondary list of HTML tag and class
                selectors.
            - **img_txt_block** (list, optional): List of tag and class selectors
                for crawling image-text pairs.
            - **implementation** (str): Crawling strategy to use. Must be one of
                ``"scan"``, ``"scroll"``, ``"onepage"``, or ``"click"``.
            - **async_** (bool, optional): Whether to use asynchronous crawling.
            - **start_page** (int, optional): Starting page index for crawling
                (0-based). Defaults to 1.
            - **sleep_time** (int, optional): Delay in seconds between requests to
                prevent being banned. Defaults to 1.
            - **save_dir** (str, optional): Directory path to save ``link.json`` and
                extracted articles.
            - **update** (bool, optional): Whether to update existing content.
                Defaults to ``True``.

    Returns:
        None: This function executes the pipeline and returns nothing.

    Notes:

        - The pipeline performs link crawling followed by content extraction.
        - Supports multiple crawling implementations (``scan``, ``scroll``,
            ``onepage``, ``click``).
        - Can operate in update mode to refresh existing content.
        - Sleep time helps avoid rate limiting or IP bans.
        - Output includes ``link.json`` and individual article files.

    """

    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.pipeline(
        dir_ = args.dir_,
        name = args.name,  
        class_ = args.class_,
        prefix = args.prefix,
        suffix = args.suffix,
        root_path = args.root_path,
        pages = args.pages,
        page_init_val = args.page_init_val,
        multiplier = args.multiplier,
        block1 = args.block1,
        block2 = args.block2,
        implementation = args.implementation,
        img_txt_block = args.img_txt_block,
        async_ = args.async_,
        start_page=args.start_page,
        sleep_time=args.sleep_time,
        save_dir=args.save_dir,
        update=args.update
        )