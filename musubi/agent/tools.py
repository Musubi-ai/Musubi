import requests
import os
from dotenv import load_dotenv
from ..utils.analyze import WebsiteNavigationAnalyzer


def google_search(
    google_engine_id: str = None,
    google_search_api: str = None,
    query: str = None,
    num_results: int = 1
):
    load_dotenv()
    """
    Get google custom search api from https://developers.google.com/custom-search/v1/overview?source=post_page-----36e5298086e4--------------------------------&hl=zh-tw.
    Also, visit https://cse.google.com/cse/all to build search engine and retrieve engine id.
    """
    if google_search_api is None:
        google_search_api = os.getenv("GOOGLE_SEARCH_API")
        if google_search_api is None:
            raise Exception(
                """google_search_api is None and cannot find it in .env file. 
                Input google_search_api or visit https://developers.google.com/custom-search/v1/overview?source=post_page-----36e5298086e4--------------------------------&hl=zh-tw to apply it."""
            )

    if google_engine_id is None:
        google_engine_id = os.getenv("GOOGLE_ENGINE_ID")
        if google_engine_id is None:
            raise Exception(
                """google_engine_id is None and cannot find it in .env file. 
                Input google_engine_id or visit https://cse.google.com/cse/all to build search engine and retrieve engine id."""
            )

    url = "https://www.googleapis.com/customsearch/v1?cx={}".format(google_engine_id) + "&key={}".format(google_search_api) + "&q={}".format(query) + "&gl=tw"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API request error")
    search_result = response.json()
    links = [search_result["items"][i]["link"] for i in range(len(search_result["items"]))]
    return links[:num_results]


def analyze_website(url):
    analyzer = WebsiteNavigationAnalyzer(url)
    navigation_type = analyzer.analyze_navigation_type()
    return navigation_type