import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    

def main():
    parser = argparse.ArgumentParser(description="Musubi CLI tool")
    parser.add_argument("name", help="your name")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()