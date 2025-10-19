import argparse
from loguru import logger
from trafilatura import fetch_url, extract
from ..agent.actions import analyze_website, get_container


def get_content(url):
    """Extract text content from a URL in markdown format.

    This function fetches content from the specified URL and extracts
    the main text content with precision-focused settings, returning
    the result in markdown format.

    Args:
        url (str): The URL of the web page to extract content from.

    Returns:
        str: The extracted text content formatted as markdown.

    Note:
        - Uses favor_precision=True for more accurate content extraction
        - Returns content in markdown format for better readability
        - Relies on fetch_url() and extract() helper functions
    """
    downloaded = fetch_url(url)
    result = extract(downloaded, favor_precision=True, output_format="markdown")
    return result


def get_command_parser(subparsers=None):
    """Create and configure argument parser for get command.

    This function creates an argument parser for the Musubi get command,
    which is used to extract various types of information from web pages
    including container structure, navigation type, and text content.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            get-related arguments and defaults set.
    """
    if subparsers is not None:
        parser = subparsers.add_parser("get")
    else:
        parser = argparse.ArgumentParser("Musubi get command")
    parser.add_argument(
        "--url", type=str, default=None, help="URL of website page to extract container for musubi pipeline function.", required=True
    )
    parser.add_argument(
        "--container", type=bool, default=None, help="Type of blocks of website page to extract text content."
    )
    parser.add_argument(
        "--type", type=bool, default=None, help="Tyoe of website page to extract text content."
    )
    parser.add_argument(
        "--text", type=bool, default=None, help="Text content of website page."
    )
    if subparsers is not None:
        parser.set_defaults(func=get_command)
    return parser


def get_command(args):
    """Execute the get command to extract information from a web page.

    This function extracts various types of information from a specified URL
    based on the provided flags. It can extract container structure
    (``block1``/``block2``), navigation type, and/or text content from the web page.

    Args:
        args (argparse.Namespace): An argparse.Namespace object containing the
            following attributes:

            - **url** (str): The URL of the web page to analyze.
            - **container** (bool, optional): If ``True``, extracts the container
                structure (``block1`` and ``block2``) from the page.
            - **type** (bool, optional): If ``True``, analyzes and returns the
                navigation type of the website.
            - **text** (bool, optional): If ``True``, extracts the main text content
                from the page in Markdown format.

    Returns:
        None: This function logs the extracted information and returns nothing.

    Raises:
        ValueError: If all three flags (``container``, ``type``, ``text``) are
            ``None``. At least one flag must be set to ``True``.

    Notes:

        - Multiple flags can be set simultaneously to extract different types of
            information in a single call.
        - Container extraction returns ``block1`` and ``block2`` HTML selectors.
        - Navigation type identifies the page's navigation pattern.
        - Text extraction uses Markdown format for better readability.
        - All results are logged using the logger.

    """
    if args.container is None and args.type is None and args.text is None:
        raise ValueError("At least one of flags '--container', '--type', and '--text' should be True.")
    if args.container is not None:
        block1, block2 = get_container(args.url)
        msg = f"block1: {block1}\nblock2: {block2}"
        logger.info(msg)
    if args.type is not None:
        navigation_type = analyze_website(args.url)
        msg = f"navigation type: {navigation_type}"
        logger.info(msg)
    if args.text is not None:
        text_content = get_content(args.url)
        msg = text_content
        logger.info(msg)
    
    