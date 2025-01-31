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


def google_search(
    query: str = None,
    num_results: int = 1,
    headless: Optional[bool] = True
):
    query = query.replace(" ", "+")
    query_url = "https://www.google.com/search?q={}&udm=14".format(query)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    options = Options()
    if headless:
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
    return urls[:num_results], root_paths[:num_results]


def analyze_website(url):
    analyzer = WebsiteNavigationAnalyzer(url)
    navigation_type = analyzer.analyze_navigation_type()
    return navigation_type


def get_container(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("body")
    possible_containers = []

    for tag in soup.find_all():
        if tag.find('a', href=True):
            class_attr = " ".join(tag.get("class", []))
            if (class_attr == "") or ("footer" in class_attr) or ("page" in class_attr):
                continue
            text = tag.get_text(separator="#", strip=True)
            try:
                if (40 > len(text) > 20) and ("#" not in text) and tag.a:
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
    
    candidates = []
    if len(possible_containers) > 0:
        counter = Counter(tuple(sublist) for sublist in possible_containers).most_common()
        max_num = max(counter, key=lambda x: x[1])[1]
        candidates = [list(item) for item, count in counter if count == max_num]
        if len(candidates) > 1:
            return candidates[-1]
        else:
            return candidates[0]