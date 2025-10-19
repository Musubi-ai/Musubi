import argparse
from .analyze import analyze_command_parser
from .env import env_command_parser
from .get import get_command_parser
from .agent import agent_command_parser
from .pipeline import pipeline_command_parser
from .crawl import crawl_link_command_parser, crawl_content_command_parser
from .start import start_all_command_parser, start_by_idx_command_parser


def build_parser():
    """Build and configure the main argument parser with all subcommands.

    This function creates the main ArgumentParser for the Musubi CLI and
    registers all available subcommands including analyze, env, get, agent,
    pipeline, crawl-link, crawl-content, start-all, and start-by-idx.

    Returns:
        argparse.ArgumentParser: The configured main parser with all
            subcommands registered and ready to parse command-line arguments.

    Note:
        The following subcommands are registered:
        - analyze: Analyze website configurations
        - env: Configure environment variables and API tokens
        - get: Extract information from web pages
        - agent: Execute AI agent operations
        - pipeline: Run content processing pipelines
        - crawl-link: Crawl and extract links from websites
        - crawl-content: Crawl and extract text content from URLs
        - start-all: Start all configured tasks
        - start-by-idx: Start specific tasks by index
    """
    parser = argparse.ArgumentParser(description="Musubi CLI tool")
    subparsers = parser.add_subparsers(dest='command')

    analyze_command_parser(subparsers)
    env_command_parser(subparsers)
    get_command_parser(subparsers)
    agent_command_parser(subparsers)
    pipeline_command_parser(subparsers)
    crawl_link_command_parser(subparsers)
    crawl_content_command_parser(subparsers)
    start_all_command_parser(subparsers)
    start_by_idx_command_parser(subparsers)

    return parser


def main():
    """Main entry point for the Musubi CLI application.

    This function parses command-line arguments and executes the appropriate
    subcommand function. If no valid subcommand is provided, it prints the
    help message and exits with status code 1.

    Returns:
        None: This function executes subcommands and returns nothing.

    Note:
        - Parses arguments using the parser built by build_parser()
        - Executes the function associated with the selected subcommand
        - Prints help and exits if no valid subcommand is specified
        - Exit code 1 indicates invalid or missing command
    """
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        exit(1)


if __name__ == "__main__":
    main()