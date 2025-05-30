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
    parser.add_argument("--dir", default=None, help="webiste name and its corresponding directory", type=str)
    parser.add_argument("--name", default=None, help="category of articels in the website", type=str)
    parser.add_argument("--class_", default=None, help="main class of the website", type=str)
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
        async_ = args.async_
        )