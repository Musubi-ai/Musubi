import argparse
from loguru import logger
from ..utils import ConfigAnalyzer


def analyze_command_parser(subparsers=None):
    """Create and configure argument parser for analyze command.

    This function creates an argument parser for the Musubi analyze command,
    which is used to analyze website configurations by domain or type.
    It can be created as either a standalone parser or as a subparser.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            analyze-related arguments and defaults set.
    """
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
    """Execute the analyze command to analyze website configuration.

    This function performs analysis on website configuration data based on
    the specified target. It supports two types of analysis: domain-based
    and type-based analysis.

    Args:
        args: An argparse.Namespace object containing the following attributes:
            website_config_path (str): Path to the website configuration JSON file.
            target (str): Type of analysis to perform. Must be either "domain"
            or "type".

    Returns:
        None: This function logs the analysis results and returns nothing.

    Raises:
        ValueError: If the target argument is not "domain" or "type".
    """
    analyzer = ConfigAnalyzer(website_config_path=args.website_config_path)
    if args.target == "domain":
        res = analyzer.domain_analyze()
        logger.info(res)
    elif args.target == "type":
        res = analyzer.type_analyze()
        logger.info(res)
    else:
        raise ValueError("The argument of flag '--target' should be one of 'domain' and 'type' but got {}".format(args.target))

