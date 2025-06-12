import argparse
from ..pipeline import Pipeline


def pipeline_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("pipeline")
    else:
        parser = argparse.ArgumentParser("Musubi pipeline command")

    # arguments for config file
    parser.add_argument("--website_config_path", default=None, help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--dir", default=None, help="webiste name and its corresponding directory", type=str, required=True)
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
    parser.add_argument("--type", default=None, help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"], required=True)
    parser.add_argument("--async_", default=True, help="asynchronous crawling or not", type=bool, required=True)
    parser.add_argument("--start_page", default=1, help="From which page to start crawling urls. 0 is first page, 1 is second page, and so forth.", type=int)
    parser.add_argument("--sleep_time", default=1, help="Sleep time to prevent ban from website.", type=int)
    parser.add_argument("--save_dir", default=None, help="Folder to save link.json and articles.", type=str)
    if subparsers is not None:
        parser.set_defaults(func=pipeline_command)
    return parser


def pipeline_command(args):
    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.pipeline(
        dir = args.dir,
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
        type = args.type,
        img_txt_block = args.img_txt_block,
        async_ = args.async_,
        start_page=args.start_page,
        sleep_time=args.sleep_time,
        save_dir=args.save_dir
        )