import argparse
from .config import config_command_parser
from .get import get_command_parser


def build_parser():
    parser = argparse.ArgumentParser(description="Musubi CLI tool")
    subparsers = parser.add_subparsers(dest='command')

    config_command_parser(subparsers)
    get_command_parser(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    main()