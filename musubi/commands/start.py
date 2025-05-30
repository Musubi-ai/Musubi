import argparse
from ..pipeline import Pipeline


def start_all_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("start-all")
    else:
        parser = argparse.ArgumentParser("Musubi start-all command")

    # arguments for config file
    parser.add_argument("--website_config_path", default=None, help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--start_idx", default=None, help="From which idx to crawl.", type=int)
    parser.add_argument("--update_pages", default=None, help="How many pages to crawl in update mode. If not None, fuction will switch to update mode and crawl specified number of pages.", type=int)
    parser.add_argument("--save_dir", default=None, help="Folder to save link.json and articles.", type=str)
    if subparsers is not None:
        parser.set_defaults(func=start_all_command)
    return parser


def start_all_command(args):
    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.start_all(
        start_idx=args.start_idx,
        update_pages=args.update_pages,
        save_dir=args.save_dir
    )


def start_by_idx_command_parser(subparsers=None):
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
    pipe = Pipeline(website_config_path=args.website_config_path)
    pipe.start_by_idx(
        idx=args.idx,
        start_page=args.strat_page,
        update_pages=args.update_pages,
        sleep_time=args.sleep_time,
        save_dir=args.save_dir
    )