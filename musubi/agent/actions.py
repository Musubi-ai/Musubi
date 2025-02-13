from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
from typing import Optional, List
from ..utils.analyze import WebsiteNavigationAnalyzer
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from collections import Counter
from ..pipeline import Pipeline


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}


def google_search(query: str = None):
    """
    Search input query on google.

    Args:
        query (`str`):
            The query you want to search on google.

    Returns:
        tuple[str, str]: A tuple containing two strings:
            - url: First URL from google search results
            - root_path: Root path (scheme + domain) extracted from the URL

    Example:
        >>> url, root_path = google_search("The New York Times")
        >>> print(url)
        'https://www.nytimes.com/international/'
        >>> print(root_paths)
        'https://www.nytimes.com'
    """
    query = query.replace(" ", "+")
    query_url = "https://www.google.com/search?q={}&udm=14".format(query)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument('--user-agent=%s' % user_agent)
    driver = Edge(options=options)
    driver.get(query_url)
    time.sleep(3)
    search_results = driver.find_elements(By.CSS_SELECTOR, 'a')
    urls = []
    root_paths = []
    for result in search_results:
        href = result.get_attribute('href')
        if href and "google.com" not in href:
            urls.append(href)
            parse = urlparse(href)
            root_path = parse.scheme + "://" + parse.netloc
            root_paths.append(root_path)

    driver.quit()
    return (urls[0], root_paths[0])


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
    """Analyzes a webpage to find potential container elements that hold link content.

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
        print(f"Failed to fetch the page: {response.status_code}")
        return ([], [])
    
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("body")
    possible_containers = []

    main_soup = soup.find("main")
    if main_soup:
        for tag in main_soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (class_attr == "") or ("footer" in class_attr) or ("page" in class_attr):
                    continue
                text = tag.get_text(separator="#", strip=True)
                try:
                    if (40 > len(text) > 15) and ("#" not in text) and tag.a:
                        possible_containers.append([tag.name, class_attr])
                    if len(possible_containers) == 0:
                        if (40 > len(text) > 15) and (len(text.split("#")) < 3) and tag.a:
                            possible_containers.append([tag.name, class_attr])
                except:
                    pass

    if len(possible_containers) == 0:
        for tag in soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (class_attr == "") or ("footer" in class_attr) or ("page" in class_attr) or ("layout" in class_attr):
                    continue
                text = tag.get_text(separator="#", strip=True)
                try:
                    if (40 > len(text) > 15) and ("#" not in text) and tag.a:
                        possible_containers.append([tag.name, class_attr])
                    if len(possible_containers) == 0:
                        if (40 > len(text) > 15) and (len(text.split("#")) < 3) and tag.a:
                            possible_containers.append([tag.name, class_attr])
                except:
                    pass

    if len(possible_containers) == 0:
        for tag in soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (class_attr == "") or ("footer" in class_attr) or ("page" in class_attr):
                    continue
                text = tag.get_text(separator="#", strip=True)
                try:
                    if (len(text) > 300) and ("#" in text) and tag.a:
                        a_tag = tag.a
                        a_class = " ".join(a_tag.get("class", []))
                        if a_class == "":
                            continue
                        possible_containers.append(["a", a_class])
                except:
                    pass

    if len(possible_containers) == 0:
        for tag in soup.find_all():
            if tag.find('a', href=True):
                class_attr = " ".join(tag.get("class", []))
                if (class_attr == "") or ("footer" in class_attr) or ("page" in class_attr):
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

    if len(possible_containers) == 0:
        menu_soup = soup.find("menu")
        a_tags = menu_soup.find_all("a")
        if len(a_tags) > 1:
            return (["menu", None], ["a", None])
    
    candidates = []
    if len(possible_containers) > 0:
        counter = Counter(tuple(sublist) for sublist in possible_containers).most_common()
        max_num = max(counter, key=lambda x: x[1])[1]
        candidates = [list(item) for item, count in counter if count == max_num]
        if len(candidates) > 1:
            return (candidates[-1], None)
        else:
            return (candidates[0], None)
        

def get_prefix_and_suffix(
    url: str = None,
    root_path: str = None
):
    """Analyzes pagination URLs to extract common prefix/suffix patterns and maximum page number.

    This function fetches a webpage and analyzes its pagination links to identify common patterns
    in the URL structure. It looks for pagination-related elements in navigation tags and anchor
    tags, then determines the common prefix and suffix used in pagination URLs.

    Args:
        url: The URL of the webpage to analyze for pagination patterns.
        root_path: Optional base URL path to prepend to relative URLs found in the page.
            If provided, will be used to construct complete URLs when prefix doesn't contain 'http'.

    Returns:
        If successful in finding pagination pattern:
            A tuple containing:
            - prefix (str): The common URL prefix before the page number
            - suffix (str): The common URL suffix after the page number
            - max_page (int): The highest page number found in the pagination links
        If unsuccessful:
            An empty list.
        
    Example:
        >>> url = "https://example.com/blog"
        >>> prefix, suffix, max_page = get_prefix_and_suffix(url)
        >>> print(f"{prefix}5{suffix}")
        https://example.com/blog/page/5/
    """
    pagination_candidates = ["pg", "pagination", "page", "pag"]
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
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
        print("Cannot find nav tag.")

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

        max_page = max([int(url.replace(prefix, "").replace(suffix, "")) for url in urls])
        return (prefix, suffix, max_page)
    else:
        return []


# Wrapper function with cleaner doxstring
def pipeline_tool(
    dir: str = None,
    name: str = None,
    class_: str = None,
    prefix: str = None,
    suffix: Optional[int] = None,
    root_path: Optional[int] = None,
    pages: int = None,
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
            The type name of data in the website.
        prefix (`str`):
            Main prefix of website. The url Musubi crawling will be formulaized as "prefix1" + str(pages) + "suffix".
        suffix (`str`, *optional*):
            Suffix of the url if exist.
        root_path (`str`, *optional*):
            Root of the url if urls in tags are presented in relative fashion.
        pages (`int`):
            Number of crawling pages.
        block1 (`list`):
            List of html tag and its class. The first element in the list should be the name of tag, e.g., "div" or "article", and the 
            second element in the list should be the class of the tag.
        block2 (`list`, *optional*):
            Second block if crawling nested structure.
        type (`str`):
            Type of crawling method to crawl urls on the website. The type should be one of the `scan`, `scroll`, `onepage`, or `click`,
            otherwise it will raise an error.
        start_page (`int`, *optional*):
            From which page to start crawling urls.
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
        "block1": block1, 
        "block2": block2, 
        "type": type,
        "start_page": start_page
    }
    pipeline.pipeline(**config_dict)