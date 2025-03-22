from typing import Optional, List
import requests
import os
from dotenv import load_dotenv, set_key
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from collections import Counter
import json
import sys
from rich.console import Console
from ...utils.analyze import WebsiteNavigationAnalyzer
from ...pipeline import Pipeline
from ...utils import is_valid_format, create_env_file


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
console = Console()


def google_search(
    query: str,
    google_search_api: Optional[str] = None,
    google_engine_id: Optional[str] = None
):
    """Searches Google using the provided query and returns the first result URL.
    
    This function performs a Google search using the Custom Search API. It requires
    valid Google Search API credentials and a Custom Search Engine ID. These can be
    provided as arguments or stored in environment variables.
    
    Args:
        query: The search query string to be sent to Google.
        google_search_api: Optional API key for Google Custom Search. If None,
            will attempt to retrieve from GOOGLE_SEARCH_API environment variable.
        google_engine_id: Optional Custom Search Engine ID. If None, will attempt
            to retrieve from GOOGLE_ENGINE_ID environment variable.
    
    Returns:
        A tuple containing:
            - The URL of the first search result.
            - The root domain of that URL (scheme + domain).
    
    Examples:
        >>> url, root_path = google_search("The New York Times")
        >>> print(url)
        'https://www.nytimes.com/international/'
        >>> print(root_path)
        'https://www.nytimes.com'
    """
    query = quote_plus(query)
    env_path = create_env_file()
    load_dotenv()
    
    # Get google custom search api from https://developers.google.com/custom-search/v1/overview?source=post_page-----36e5298086e4--------------------------------&hl=zh-tw.
    # Also, visit https://cse.google.com/cse/all to build search engine and retrieve engine id.
    
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

    url = "https://www.googleapis.com/customsearch/v1?cx={}".format(google_engine_id) + "&key={}".format(google_search_api) + "&q={}".format(query) + "&udm=14"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API request error")
    search_result = response.json()
    links = [search_result["items"][i]["link"] for i in range(len(search_result["items"]))]
    res_url = links[0]
    parse = urlparse(res_url)
    root_path = parse.scheme + "://" + parse.netloc


    if google_search_api != os.getenv("GOOGLE_SEARCH_API"):
        set_key(env_path, key_to_set="GOOGLE_SEARCH_API", value_to_set=google_search_api)
    if google_engine_id != os.getenv("GOOGLE_ENGINE_ID"):
        set_key(env_path, key_to_set="GOOGLE_ENGINE_ID", value_to_set=google_engine_id)

    return (res_url, root_path)


def analyze_website(url: str) -> str:
    """
    Analyzes a website's navigation mechanism to determine the optimal crawling method.
    
    This function examines the website structure and navigation patterns to suggest
    the most appropriate crawling strategy from the following options:
    - 'scan': Website uses page numbers in URL (e.g., /page/1/, /page/2/)
    - 'click': Navigation requires clicking through elements (e.g., "Next" buttons)
    - 'scroll': Content loads dynamically through infinite scrolling
    - 'onepage': All content is available on a single page
    
    Args:
        url (str): The target website URL to analyze
            
    Returns:
        navigation_type (str): The recommended crawling method, one of:
            'scan', 'click', 'scroll', or 'onepage'
            
    Examples:
        >>> url = "https://takao.tw/page/2/"
        >>> method = analyze_website(url)
        >>> print(method)
        'scan'
    """
    analyzer = WebsiteNavigationAnalyzer(url)
    navigation_type = analyzer.analyze_navigation_type()
    return navigation_type


def get_container(url: str):
    """
    Analyzes a webpage to find potential container elements that hold link content.

    This function scrapes a webpage and searches for HTML elements that likely contain
    meaningful link content based on various heuristics like text length, presence of links,
    and class attributes. It prioritizes containers within the <main> tag and applies
    progressively looser criteria if no suitable containers are found.

    Args:
        url: A string containing the URL of the webpage to analyze.

    Returns:
        A tuple containing two lists:
        - First list: Contains [element_name, class_name] of the most common container,
          or ["menu", None] if only a menu structure is found.
        - Second list: Contains [child_element_name, class_name] if a specific child
          element is identified, or None if no child element is needed.
    """
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        console.log(f"Failed to fetch the page: {response.status_code}")
        return ([], None)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("body")
    possible_containers = []
    ignore_class = ["left", "right", "footer", "page", "layout", "nav"]

    main_soup = soup.find("main")
    if main_soup:
        for tag in main_soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (any(cls in class_attr for cls in ignore_class)) or (class_attr == ""):
                    continue
                text = tag.get_text(separator="#", strip=True)
                try:
                    if (len(text) > 15) and ("#" not in text) and tag.a:
                        possible_containers.append([tag.name, class_attr])
                    if len(possible_containers) == 0:
                        if (len(text) > 15) and (len(text.split("#")) < 3) and tag.a:
                            possible_containers.append([tag.name, class_attr])
                except:
                    pass

    if len(possible_containers) == 0:
        for tag in soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (any(cls in class_attr for cls in ignore_class)) or (class_attr == ""):
                    continue
                text = tag.get_text(separator="#", strip=True)
                try:
                    if (len(text) > 15) and ("#" not in text) and tag.a:
                        possible_containers.append([tag.name, class_attr])
                    if len(possible_containers) == 0:
                        if (len(text) > 15) and (len(text.split("#")) < 3) and tag.a:
                            possible_containers.append([tag.name, class_attr])
                except:
                    pass

    if len(possible_containers) < 5:
        for tag in soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (any(cls in class_attr for cls in ignore_class)) or  (class_attr == ""):
                    continue
                text = tag.get_text(separator="#", strip=True)
                text_list = text.split("#")
                len_condition = any(len(item) > 15 for item in text_list)
                try:
                    if tag.a and tag.a.img and (text != "") and len_condition:
                        a_tag = tag.a
                        possible_containers.append([tag.name, class_attr])
                except:
                    pass

                try:
                    if (len(text) > 300) and ("#" in text) and tag.a.get_text():
                        a_list = tag.find_all("a", href=True)
                        for a_element in a_list:
                            text = a_element.get_text()
                            if len(text) > 10:
                                # a_tag = tag.a
                                # a_class = " ".join(a_tag.get("class", []))
                                a_class = " ".join(a_element.get("class", []))
                                if a_class == "":
                                    continue
                                possible_containers.append(["a", a_class])
                except:
                    pass

    if len(possible_containers) == 0:
        try:
            menu_soup = soup.find("menu")
            a_tags = menu_soup.find_all("a")
            if len(a_tags) > 1:
                return (["menu", None], ["a", None])
        except:
            return ([None, None], [None, None])
    
    candidates = []
    if len(possible_containers) > 0:
        counter = Counter(tuple(sublist) for sublist in possible_containers).most_common()
        max_num = max(counter, key=lambda x: x[1])[1]
        candidates = [list(item) for item, count in counter if count == max_num]
        if len(candidates) > 1:
            return (candidates[-1], None)
        else:
            return (candidates[0], None)
        

def get_page_info(
    url: str = None,
    root_path: str = None
):
    """
    Analyzes webpage pagination to extract URL patterns and page number information.

    Fetches a webpage and analyzes its pagination links to determine the URL structure
    used for pagination. It searches for pagination-related elements within navigation
    and anchor tags to extract common patterns in the URLs.

    Args:
        url: URL of the webpage to analyze.
        root_path: Base URL path to prepend to relative URLs. Required when the
            extracted prefix doesn't contain 'http'. If the root_path ends with '/'
            and prefix starts with '/', the extra slash will be handled appropriately.

    Returns:
        tuple:
            A 5-element tuple containing:
            - prefix (str): Common URL prefix before page number
            - suffix (str): Common URL suffix after page number
            - max_page (int): Highest page number found
            - page_init_val (int): Starting page number
            - multiplier (int): Increment between page numbers
            If no pagination is found, returns (None, None, None, None, None)

    Examples:
        >>> url = "https://example.com/blog"
        >>> prefix, suffix, max_page, page_init_val, multiplier = get_page_info(url)
        >>> print(f"{prefix}5{suffix}")
        https://example.com/blog/page/5/
    """
    pagination_candidates = ["pg", "pagination", "page", "pag"]
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        console.log(f"Failed to fetch the page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    nav_soup = soup.find_all("nav")
    urls = []
    try:
        for nav_node in nav_soup:
            nav_class = nav_node.get("class")
            nav_class = " ".join(nav_class)

            a_tags = nav_node.find_all("a")
            for a_tag in a_tags:
                href = a_tag.get("href")
                if any(item in href for item in pagination_candidates):
                    urls.append(href)
    except:
        console.log("Cannot find nav tag.")

    if len(urls) == 0:
        a_soup = soup.find_all("a", href=True)
        for a_tag in a_soup:
            href = a_tag.get("href")
            if any(item in href for item in pagination_candidates):
                    urls.append(href)

    if len(urls) > 2:
        for i in range(len(urls)-1):
            url1 = urls[i]
            url2 = urls[i+1]
            length = len(url1)
            suffix_loc = length - 1
            prefix_loc = 1
            done_searching_suffix = False
            done_searching_prefix = False
            for j in range(length):
                if not done_searching_suffix:
                    suffix1 = url1[suffix_loc-j:length]
                    suffix2 = url2[suffix_loc-j:length]
                    if suffix1 != suffix2:
                        suffix = url1[suffix_loc-j+1:length]
                        done_searching_suffix = True
                if not done_searching_prefix:
                    prefix1 = url1[:prefix_loc+j]
                    prefix2 = url2[:prefix_loc+j]
                    if prefix1 != prefix2:
                        prefix = url1[:prefix_loc+j-1]
                        done_searching_prefix = True
                if done_searching_prefix and done_searching_suffix:
                    break
            if prefix and suffix:
                if "http" not in prefix:
                    if ("http" in root_path) and (root_path[-1]=="/") and (prefix[0]=="/"):
                        prefix = root_path[:-1] + prefix
                    elif ("http" in root_path) and (root_path[-1]!="/") and (prefix[0]!="/"):
                        prefix = root_path + "/" + prefix
                    elif "http" in root_path:
                        prefix = root_path + prefix
                    else:
                        raise Exception("Cannot find suitable prefix")
                break
        pages = [int(url.replace(prefix, "").replace(suffix, "")) for url in urls if is_valid_format(s=url, prefix=prefix, suffix=suffix)]
        if suffix == "":
            suffix = None
        max_page = max(pages)
        if min(pages) == 2:
            page_init_val = 1
        elif min(pages)==1:
            page_init_val = 0
        try:
            multiplier = abs(pages[1] - pages[0])
        except:
            multiplier = 1

        return (prefix, suffix, max_page, page_init_val, multiplier)
    else:
        return (None, None, None, None, None)
    

def final_answer(text: str = None):
    """
    Parses and processes the final inference result from Musubi agent.

    This function takes the raw text output from Musubi agent inference,
    strips any whitespace, and attempts to parse it as JSON. The parsed 
    JSON is then validated to ensure it contains the required keys for 
    further processing.

    Args:
        text (str, optional): Raw text output from the Musubi agent inference.
            Defaults to None.

    Returns:
        dict: The parsed JSON data structure containing the processed inference result.
    """
    try:
        data = json.loads(text.strip())
    except json.JSONDecodeError as e:
        console.log("JSON parser error:", e)
        sys.exit(1)
    expected_keys = {
    "dir", "name", "class_", "prefix", "suffix",
    "root_path", "pages", "block1", "block2",
    "type", "start_page"
    }
    actual_keys = set(data.keys())
    missing_keys = expected_keys - actual_keys
    extra_keys = actual_keys - expected_keys
    if missing_keys or extra_keys:
        console.log("missing keys:", missing_keys)
        console.log("extra keys:", extra_keys)
        raise ValueError("Parsed dictionary doesn't match with necessray format for implementing `pipeline_tool` function.")

    return data


# Wrapper function with cleaner doxstring
def pipeline_tool(
    dir: str = None,
    name: str = None,
    class_: str = None,
    prefix: str = None,
    suffix: Optional[int] = None,
    root_path: Optional[int] = None,
    pages: int = None,
    page_init_val: Optional[int] = 1,
    multiplier: Optional[int] = 1,
    block1: List[str] = None,
    block2: Optional[List[str]] = None,
    type: str = None,
    start_page: Optional[int] = 0
):
    """
    Main function to add new website into config json file and scrape website articles.

    Args:
        dir (`str`):
            Folder name of new website.
        name (`str`):
            Subfolder name under the website.
        class_ (`str`):
                The type of data in the website. The most general case to use this argument is using the main language of website name, e.g., English, 中文,...
        prefix (`str`):
            Main prefix of website. The url Musubi crawling will be formulaized as "prefix1" + str((page_inint_val + pages) * multiplier) + "suffix".
        suffix (`str`, *optional*):
            Suffix of the url if exist.
        root_path (`str`, *optional*):
            Root of the url if urls in tags are presented in relative fashion.
        pages (`int`):
            Number of crawling pages.
        page_init_val (`int`, default=1):
            Initial value of page.
        multiplier (`int`, default=1):
            Multiplier of page.
        block1 (`list`):
            List of html tag and its class. The first element in the list should be the name of tag, e.g., "div" or "article", and the 
            second element in the list should be the class of the tag.
        block2 (`list`, *optional*):
            Second block if crawling nested structure.
        type (`str`):
            Type of crawling method to crawl urls on the website. The type should be one of the `scan`, `scroll`, `onepage`, or `click`,
            otherwise it will raise an error.
        start_page (`int`, *optional*, default=0):
            From which page to start crawling urls. 0 is first page, 1 is second page, and so forth.
    """
    pipeline = Pipeline()
    config_dict = {
        "dir": dir, 
        "name": name, 
        "class_": class_, 
        "prefix": prefix, 
        "suffix": suffix, 
        "root_path": root_path, 
        "pages": pages,
        "page_init_val": page_init_val,
        "multiplier": multiplier,
        "block1": block1, 
        "block2": block2, 
        "type": type,
        "start_page": start_page
    }
    pipeline.pipeline(**config_dict)