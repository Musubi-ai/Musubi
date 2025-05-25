import argparse
from rich.console import Console
from trafilatura import fetch_url, extract
from ..agent.actions import analyze_website, get_container


def get_content(url):
    downloaded = fetch_url(url)
    result = extract(downloaded, favor_precision=True, output_format="markdown")
    return result


def get_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("get")
    else:
        parser = argparse.ArgumentParser("Musubi get command")
    parser.add_argument(
        "--url", type=str, default=None, help="URL of website page to extract container for musubi pipeline function.", required=True
    )
    parser.add_argument(
        "--container", type=bool, default=None, help="URL of website page to extract text content."
    )
    parser.add_argument(
        "--type", type=bool, default=None, help="URL of website page to extract text content."
    )
    parser.add_argument(
        "--text", type=bool, default=None, help="URL of website page to extract text content."
    )
    if subparsers is not None:
        parser.set_defaults(func=get_command)
    return parser


def get_command(args):
    console = Console()
    if args.container is None and args.type is None and args.text is None:
        raise ValueError("At least one of flags '--container', '--type', and '--text' should be True.")
    if args.container is not None:
        block1, block2 = get_container(args.url)
        msg = f"block1: {block1}\nblock2: {block2}"
        console.log(msg)
    if args.type is not None:
        navigation_type = analyze_website(args.url)
        msg = f"navigation type: {navigation_type}"
        console.log(msg)
    if args.text is not None:
        text_content = get_content(args.url)
        msg = text_content
        console.log(msg)
    
    