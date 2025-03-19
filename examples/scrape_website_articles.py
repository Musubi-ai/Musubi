"""
Example of scraping articles in 'Craft and Criticism' category of Literary Hub.
"""
from musubi.pipeline import Pipeline
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info
)


def main(
    query: str,
    website_config_path: str,
    dir: str,
    name: str,
    class_: str
):
    url, root_path = google_search(query)
    website_type = analyze_website(url)
    block1, block2 = get_container(url)
    prefix, suffix, max_pages, page_init_val, multiplier = get_page_info(url=url, root_path=root_path)
    pipeline_kwargs = {
        "dir": dir, 
        "name": name, 
        "class_": class_, 
        "prefix": prefix, 
        "suffix": suffix, 
        "root_path": root_path, 
        "pages": max_pages,
        "page_init_val": page_init_val,
        "multiplier": multiplier,
        "block1": block1, 
        "block2": block2, 
        "type": website_type,
    }
    pipeline = Pipeline(website_config_path=website_config_path)
    pipeline.pipeline(**pipeline_kwargs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--website_config_path", default=r"config\websites.json", help="webiste config file", type=str)
    parser.add_argument("--query", default="Literary Hub Craft and Criticism", help="Query to search website on google", type=str)
    parser.add_argument("--dir", default="Literary_Hub", help="The name of website and its corresponding directory", type=str)
    parser.add_argument("--name", default="Craft and Criticism", help="Category of articels in the website", type=str)
    parser.add_argument("--class_", default="English", help="Main class of the website", type=str)
    args = parser.parse_args()

    main(
        query=args.query,
        website_config_path=args.website_config_path,
        dir=args.dir,
        name=args.name,
        class_=args.class_
    )
