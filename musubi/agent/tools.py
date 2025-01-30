from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
from typing import Optional
from ..utils.analyze import WebsiteNavigationAnalyzer


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
    for result in search_results:
        href = result.get_attribute('href')
        if href and "google.com" not in href:
            urls.append(href)

    driver.quit()
    return urls[:num_results]


def analyze_website(url):
    analyzer = WebsiteNavigationAnalyzer(url)
    navigation_type = analyzer.analyze_navigation_type()
    return navigation_type