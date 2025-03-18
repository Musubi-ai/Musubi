"""
Example of scraping articles in 'fiction and poetry' category of Literary Hub.
"""
from musubi.pipeline import Pipeline
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info
)


url, root_path = google_search("The New York Times")




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # arguments for config file
    parser.add_argument("--website_config_path", default=r"config\websites.json", help="webiste config file", type=str)
    # arguments for add mode
    parser.add_argument("--dir", default="Literary_Hub", help="The name of website and its corresponding directory", type=str)
    parser.add_argument("--name", default="fiction_and_poetry", help="Category of articels in the website", type=str)
    parser.add_argument("--class_", default="English", help="Main class of the website", type=str)
    parser.add_argument("--prefix", default="https://views.learneating.com/category/sport-nutrition/", help="prefix of url", type=str)
    parser.add_argument("--suffix", default=None, help="suffix of url", type=str)
    parser.add_argument("--root_path", default=None, help="root path of root website", type=str)
    parser.add_argument("--pages", default=1, help="pages of websites", type=int)
    parser.add_argument("--page_init_val", default=1, help="Initial value of pages", type=int)
    parser.add_argument("--multiplier", default=1, help="Multiplier of pages", type=int)
    parser.add_argument("--block1", default=['h2', 'entry-title'], help="main list of tag and class", type=list)
    parser.add_argument("--block2", default=None, help="sub list of tag and class", type=list)
    parser.add_argument("--type", default="onepage", help="way of crawling websites", type=str, choices=["scan", "scroll", "onepage", "click"])
    parser.add_argument("--async_", default=True, help="asynchronous crawling or not", type=bool)
    args = parser.parse_args()

    print(url)
    print(root_path)
