import argparse
from loguru import logger
from ..utils import ConfigAnalyzer


def analyze_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("analyze")
    else:
        parser = argparse.ArgumentParser("Musubi analyze command")

    parser.add_argument(
        "--website_config_path", type=str, default=None, help="Path of website config json file"
    )
    parser.add_argument(
        "--target", type=str, default="domain", help="Analyzing target", choices=["domain", "type"]
    )
    if subparsers is not None:
        parser.set_defaults(func=analyze_command)
    return parser


def analyze_command(args):
    analyzer = ConfigAnalyzer(website_config_path=args.website_config_path)
    if args.target == "domain":
        res = analyzer.domain_analyze()
        logger.info(res)
    elif args.target == "type":
        res = analyzer.type_analyze()
        logger.info(res)
    else:
        raise ValueError("The argument of flag '--target' should be one of 'domain' and 'type' but got {}".format(args.target))

