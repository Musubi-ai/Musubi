from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
from typing import Optional
from ..utils.analyze import WebsiteNavigationAnalyzer
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from collections import Counter


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
        
    Note:
        The analysis is performed using the WebsiteNavigationAnalyzer class
        which examines the DOM structure and navigation patterns.
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

    Notes:
        The function uses several strategies to identify containers:
        1. Looks for elements in <main> with links and specific text length (15-40 chars)
        2. Searches entire body if no containers found in <main>
        3. Checks for elements with longer text (>300 chars) and link tags
        4. Looks for elements containing links with images
        5. Falls back to menu structure if no other containers found

    The function filters out elements with empty class attributes or classes containing
    "footer", "page", or "layout" terms.
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

    Raises:
        Exception: If a suitable prefix cannot be constructed from the provided root_path.
        
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