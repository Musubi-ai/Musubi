import os
import requests
from abc import ABC, abstractmethod
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from loguru import logger
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional
import orjson
import time
from tqdm import tqdm
from .utils import get_root_path


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


class BaseCrawl(ABC):
    def __init__(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.root_path = root_path
        self.pages = pages
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        self.sleep_time = sleep_time
        self.page_init_val = page_init_val
        self.multiplier = multiplier

    @abstractmethod
    def crawl_link(self):
        ...

    @abstractmethod
    def check_link_result(self):
        ...


class Scan(BaseCrawl):
    """A web scraper for extracting URLs from paginated websites.

    This class extends BaseCrawl to scan through multiple pages of a website
    and extract URLs based on specified HTML block selectors. It supports
    various pagination patterns and can handle both absolute and relative URLs.

    Args:
        prefix (str): The base URL or prefix for generating page URLs.
        suffix (str, optional): The suffix to append after the page number in URLs.
            Defaults to None.
        root_path (str, optional): The root domain path for constructing absolute
            URLs from relative links. Defaults to None.
        pages (int, optional): Number of pages to scan. If set to 1, only the
            prefix URL is scanned. Defaults to None.
        block1 (list): List containing [tag_name, class_name] for the primary
            HTML block selector.
        block2 (list, optional): List containing [tag_name, class_name] for a
            nested HTML block selector. Defaults to None.
        url_path (str, optional): Path to save extracted URLs as JSONL.
            Defaults to None.
        sleep_time (int, optional): Number of seconds to sleep between requests.
            Defaults to None.
        page_init_val (int, optional): Initial value for page numbering.
            Defaults to 1.
        multiplier (int, optional): Multiplier for page numbers in URL generation.
            Defaults to 1.
        **kwargs: Additional keyword arguments passed to BaseCrawl.

    Note:
        - Page URLs are generated as: prefix + (page_init_val + i) * multiplier + suffix
        - If pages is 1, only the prefix URL is used without pagination.
        - The class automatically handles relative and absolute URL conversion.
    """
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        page_init_val: Optional[int] = 1,
        multiplier: Optional[int] = 1,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time, page_init_val, multiplier)
        if pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if suffix:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) + self.suffix for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str((self.page_init_val + i) * self.multiplier) for i in range(self.pages)]

        self.length = len(self.pages_lst)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")

    def get_urls(self, page):
        """Extract URLs from a single page based on HTML block selectors.

        This method fetches a page, parses its HTML content, and extracts URLs
        from elements matching the specified block selectors. It handles both
        absolute and relative URLs, converting relative URLs to absolute ones
        when necessary.

        Args:
            page (str): The URL of the page to scrape.

        Returns:
            list: A list of extracted URLs (as strings) from the page.

        Raises:
            ValueError: If root_path is provided but does not contain 'http'.

        Note:
            - If block2 is specified, the method first finds elements matching
              block1, then searches for block2 elements within them.
            - The method automatically handles URL path concatenation, ensuring
              proper '/' separators between root_path and relative URLs.
            - If root_path is not provided, it is automatically extracted from
              the page URL.
        """
        link_list = []
        r = requests.get(page, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")
        if self.block2:
            blocks = soup.find(self.block1[0], class_=self.block1[1])
            blocks = blocks.find_all(self.block2[0], class_=self.block2[1])
        else:
            blocks = soup.find_all(self.block1[0], class_=self.block1[1])

        for block in blocks:
            if self.root_path:
                if self.plural_a_tag:
                    if "http" not in block["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block["href"]
                    else:
                        link = block["href"]
                else:
                    if "http" not in block.a["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block.a["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block.a["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block.a["href"]
                    else:
                        link = block.a["href"]
            else:
                if self.plural_a_tag:
                    if "http" in block["href"]:
                        link = block["href"]
                    else:
                        root_path = get_root_path(page)
                        if block["href"][0] == "/":
                            link = root_path + block["href"]
                        else:
                            link = root_path + "/" + block["href"]
                else:
                    if "http" in block.a["href"]:
                        link = block.a["href"]
                    else:
                        root_path = get_root_path(page)
                        if block.a["href"][0] == "/":
                            link = root_path + block.a["href"]
                        else:
                            link = root_path + "/" + block.a["href"]
            link_list.append(link)
        return link_list
    
    def crawl_link(self, start_page: int=0):
        """Check and print the first extracted URL from the first page.

        This method extracts URLs from the first page in pages_lst and prints
        the first URL to stdout. Useful for testing and verifying that the
        URL extraction is working correctly.

        Returns:
            None: Prints the first extracted URL to stdout.
        """
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        
        for i in tqdm(range(start_page, self.length), desc="Crawling urls..."):
            page = self.pages_lst[i]
            link_list = self.get_urls(page=page)
            for link in link_list:
                if url_list and link in url_list:
                    continue 
                dictt = {"link": link}
                with open(self.url_path, "ab") as file:
                    file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        page = self.pages_lst[0]
        link_list = self.get_urls(page=page)
        print(link_list[0])


class Scroll(BaseCrawl):
    """A web scraper for extracting URLs from infinite-scroll or dynamically loaded websites.

    This class extends BaseCrawl to handle websites that load content dynamically
    through scrolling. It uses Selenium WebDriver to simulate scrolling behavior
    and extract URLs from elements that appear after scrolling.

    Args:
        prefix (str): The URL of the page to scrape.
        suffix (str, optional): Not used in this class but kept for compatibility
            with BaseCrawl. Defaults to None.
        root_path (str, optional): The root domain path for constructing absolute
            URLs from relative links. Defaults to None.
        pages (int, optional): Number of times to scroll down the page to load
            more content. Defaults to None.
        block1 (list): List containing [tag_name, class_name] for the HTML block
            selector containing target URLs.
        block2 (list, optional): Not used in this class but kept for compatibility
            with BaseCrawl. Defaults to None.
        url_path (str, optional): Path to save extracted URLs as JSONL.
            Defaults to None.
        sleep_time (int, optional): Number of seconds to wait between scroll actions
            to allow content to load. Defaults to 5.
        **kwargs: Additional keyword arguments passed to BaseCrawl.

    Note:
        - This class requires Microsoft Edge WebDriver to be installed.
        - The browser runs in headless mode by default.
        - Scrolling stops automatically if the page height doesn't change,
          indicating no more content to load.
    """
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = 5,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.scroll_time = pages

    def browse_website(self):
        """Initialize and navigate to the target website using Edge WebDriver.

        This method creates a headless Edge browser instance with optimized
        settings and navigates to the URL specified in prefix. It waits for
        the initial page load before returning.

        Returns:
            None: Sets self.driver with the initialized WebDriver instance.

        Note:
            - The browser runs in headless mode (no visible window).
            - Window size is set to 1920x1080 for consistent rendering.
            - GPU acceleration is disabled for better compatibility in headless mode.
            - Waits for sleep_time seconds after loading the page.
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = Edge(options=options)
        self.driver.get(self.prefix)
        time.sleep(self.sleep_time)

    def scroll(
        self,
        scroll_time: int = None
    ):
        """Scroll down the page multiple times to load dynamic content.

        This method simulates user scrolling by repeatedly scrolling to the bottom
        of the page. It stops early if the page height stops increasing, indicating
        no more content is loading.

        Args:
            scroll_time (int, optional): Number of times to scroll down. If None,
                uses self.scroll_time. Defaults to None.

        Returns:
            None: The page is scrolled and content is loaded in the WebDriver.

        Note:
            - Each scroll action scrolls to the absolute bottom of the page.
            - Waits sleep_time seconds between scrolls for content to load.
            - A progress bar displays the scrolling progress.
            - Automatically stops if page height remains unchanged, even if
              scroll_time hasn't been reached.
        """
        n = 0
        scroll_time = scroll_time if scroll_time is not None else self.scroll_time
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        with tqdm(total=scroll_time, desc="Scrolling") as pbar:
            while n < scroll_time:
                self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
                n += 1
                time.sleep(self.sleep_time)
                pbar.update(1)

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

    def crawl_link(self):
        """Crawl and save URLs from the scrollable page.

        This method opens the website, scrolls to load all content, extracts URLs
        from elements matching the specified block selector, and saves them to a
        JSONL file. Already extracted URLs are automatically skipped.

        Returns:
            None: URLs are saved to the file specified by url_path.

        Note:
            - Initializes the browser and performs full scrolling automatically.
            - Handles both absolute and relative URLs, converting relative URLs
              to absolute ones when necessary.
            - If the target block is not an anchor tag, searches for anchor tags
              within the block.
            - Skips duplicate URLs if url_path already exists.
            - Each URL is saved as a JSON object with a 'link' field.
        """
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None
        self.browse_website()
        self.scroll()
        elements = self.driver.find_elements(By.TAG_NAME, self.block1[0])

        for item in elements:
            class_ = item.get_attribute("class")
            if (class_ == self.block1[1]):
                if self.block1[0] != "a":
                    a = item.find_element(By.TAG_NAME, "a")
                    url = a.get_attribute("href")
                else:
                    url = item.get_attribute("href")
                if self.root_path:
                    if self.root_path[-1] == url[0] == "/":
                        self.root_path = self.root_path[:-1]
                    elif (self.root_path[-1] != "/") and (url[0] != "/"):
                        self.root_path = self.root_path + "/"
                    elif ("http" in self.root_path) and ("http" in url):
                        self.root_path = ""
                    url = self.root_path + url
                else:
                    if "http" not in url:
                        root_path = get_root_path(self.prefix)
                        if url[0] == "/":
                            url = root_path + url
                        else:
                            url = root_path + "/" + url
                if url_list and (url in url_list):
                    continue 
                dictt = {"link": url}

                with open(self.url_path, "ab") as file:
                    file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        """Check and print extracted URLs from a single scroll action.

        This method opens the website, performs a single scroll, extracts URLs
        from the specified block, and prints them to stdout. Useful for testing
        and verifying that URL extraction is working correctly.

        Returns:
            None: Prints a list of dictionaries containing extracted URLs to stdout.

        Note:
            - Only scrolls once (scroll_time=1) for quick testing.
            - Finds all anchor tags within elements matching the block selector.
            - Does not check for duplicates or save to file.
        """
        self.browse_website()
        self.scroll(scroll_time = 1)
        element = self.driver.find_element(By.CLASS_NAME, self.block1[1])
        elements = element.find_elements(By.TAG_NAME, "a")

        check_list = []

        for item in elements:
            url = item.get_attribute("href")
            if self.root_path:
                url = self.root_path + url
            dictt = {"link": url}
            check_list.append(dictt)
        print(check_list)


class OnePage(BaseCrawl):
    """A web scraper for extracting URLs from a single static page.

    This class extends BaseCrawl to handle simple cases where all target URLs
    are located on a single page without pagination or dynamic loading. It parses
    the HTML content and extracts URLs based on specified block selectors.

    Args:
        prefix (str): The URL of the page to scrape.
        suffix (str, optional): Not used in this class but kept for compatibility
            with BaseCrawl. Defaults to None.
        root_path (str, optional): The root domain path for constructing absolute
            URLs from relative links. Defaults to None.
        pages (int, optional): Not used in this class but kept for compatibility
            with BaseCrawl. Defaults to None.
        block1 (list): List containing [tag_name, class_name] for the primary
            HTML block selector.
        block2 (list, optional): List containing [tag_name, class_name] for a
            nested HTML block selector. Defaults to None.
        url_path (str, optional): Path to save extracted URLs as JSONL.
            Defaults to None.
        sleep_time (int, optional): Not used in this class but kept for
            compatibility with BaseCrawl. Defaults to None.
        **kwargs: Additional keyword arguments passed to BaseCrawl.

    Note:
        - This class is optimized for single-page URL extraction without the
          overhead of pagination or browser automation.
        - Use Scan class for multi-page scraping or Scroll class for dynamic
          content loading.
    """
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = None,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")

    def get_urls(self):
        """Extract all URLs from the page based on HTML block selectors.

        This method fetches the page specified in prefix, parses its HTML content,
        and extracts URLs from elements matching the specified block selectors.
        It handles both absolute and relative URLs, converting relative URLs to
        absolute ones when necessary.

        Returns:
            list: A list of extracted URLs (as strings) from the page.

        Raises:
            ValueError: If root_path is provided but does not contain 'http'.

        Note:
            - If block2 is specified, the method first finds the element matching
              block1, then searches for all block2 elements within it.
            - The method automatically handles URL path concatenation, ensuring
              proper '/' separators between root_path and relative URLs.
            - If root_path is not provided, it is automatically extracted from
              the prefix URL.
        """
        link_list = []
        r = requests.get(self.prefix, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")

        if self.block2:
            blocks = soup.find(self.block1[0], class_=self.block1[1])
            blocks = blocks.find_all(self.block2[0], class_=self.block2[1])
        else:
            blocks = soup.find_all(self.block1[0], class_=self.block1[1])

        for block in blocks:
            if self.root_path:
                if self.plural_a_tag:
                    if "http" not in block["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block["href"]
                    else:
                        link = block["href"]
                else:
                    if "http" not in block.a["href"]:
                        if "http" in self.root_path:
                            if self.root_path[-1] == block.a["href"][0] == "/":
                                self.root_path = self.root_path[:-1]
                            elif (self.root_path[-1] != "/") and (block.a["href"][0] != "/"):
                                self.root_path = self.root_path + "/"
                        else:
                            raise ValueError("Wrong value of root_path.")
                        link = self.root_path + block.a["href"]
                    else:
                        link = block.a["href"]
            else:
                if self.plural_a_tag:
                    if "http" in block["href"]:
                        link = block["href"]
                    else:
                        root_path = get_root_path(self.prefix)
                        if block["href"][0] == "/":
                            link = root_path + block["href"]
                        else:
                            link = root_path + "/" + block["href"]
                else:
                    if "http" in block.a["href"]:
                        link = block.a["href"]
                    else:
                        root_path = get_root_path(self.prefix)
                        if block.a["href"][0] == "/":
                            link = root_path + block.a["href"]
                        else:
                            link = root_path + "/" + block.a["href"]
            link_list.append(link)

        return link_list
    
    def crawl_link(self):
        """Crawl and save URLs from the single page.

        This method extracts all URLs from the page using get_urls() and saves
        them to a JSONL file. Already extracted URLs are automatically skipped
        to avoid duplicates.

        Returns:
            None: URLs are saved to the file specified by url_path.

        Note:
            - Each URL is saved as a JSON object with a 'link' field.
            - If url_path already exists, the method checks for existing URLs
              and skips them to prevent duplicates.
            - Unlike Scan class, this method does not iterate through multiple
              pages or show a progress bar.
        """
        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        link_list = self.get_urls()
        for link in link_list:
            if url_list and link in url_list:
                continue 
            dictt = {"link": link}
            with open(self.url_path, "ab") as file:
                file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

    def check_link_result(self):
        """Check and print all extracted URLs from the page.

        This method extracts all URLs from the page using get_urls() and prints
        the complete list to stdout. Useful for testing and verifying that the
        URL extraction is working correctly.

        Returns:
            None: Prints a list of all extracted URLs to stdout.

        Note:
            - Unlike the Scan class check method which only prints the first URL,
              this method prints all extracted URLs.
            - Does not save URLs to file.
        """
        link_list = self.get_urls()
        print(link_list)


class Click(BaseCrawl):
    """A web scraper for extracting URLs from pages with 'Load More' or pagination buttons.

    This class extends BaseCrawl to handle websites that require clicking a button
    (e.g., "Load More", "Next Page") to reveal additional content. It uses Selenium
    WebDriver to simulate button clicks and extract URLs from newly loaded elements.

    Args:
        prefix (str): The URL of the page to scrape.
        suffix (str, optional): Not used in this class but kept for compatibility
            with BaseCrawl. Defaults to None.
        root_path (str, optional): The root domain path for constructing absolute
            URLs from relative links. Defaults to None.
        pages (int, optional): Number of times to click the load button to reveal
            more content. Defaults to None.
        block1 (list): List containing [tag_name, class_name] for the HTML block
            selector containing target URLs.
        block2 (list, optional): List containing [tag_name, class_name] for the
            button element to click. Required for this class. Defaults to None.
        url_path (str, optional): Path to save extracted URLs as JSONL.
            Defaults to None.
        sleep_time (int, optional): Number of seconds to wait after each click
            to allow content to load. Defaults to 5.
        **kwargs: Additional keyword arguments passed to BaseCrawl.

    Note:
        - This class requires Microsoft Edge WebDriver to be installed.
        - The browser runs in headless mode by default.
        - block2 must be specified to identify the clickable button element.
        - The method attempts JavaScript click first, then falls back to standard
          click if that fails.
    """
    def __init__(
        self, 
        prefix: str,
        suffix: Optional[str] = None,
        root_path: Optional[str] = None,
        pages: Optional[int] = None,
        block1: List[str] = None,
        block2: Optional[List[str]] = None,
        url_path: Optional[str] = None,
        sleep_time: Optional[int] = 5,
        **kwargs
    ):
        super().__init__(prefix, suffix, root_path, pages, block1, block2, url_path, sleep_time)
        self.click_time = pages

    def browse_website(self):
        """Initialize and navigate to the target website using Edge WebDriver.

        This method creates a headless Edge browser instance with optimized
        settings and navigates to the URL specified in prefix. It waits for
        the initial page load before returning.

        Returns:
            None: Sets self.driver with the initialized WebDriver instance.

        Note:
            - The browser runs in headless mode (no visible window).
            - Window size is set to 1920x1080 for consistent rendering.
            - GPU acceleration is disabled for better compatibility in headless mode.
            - Waits for sleep_time seconds after loading the page if sleep_time
              is specified.
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = Edge(options=options)
        self.driver.get(self.prefix)
        if self.sleep_time:
            time.sleep(self.sleep_time)

    def crawl_link(
        self,
        click_time: int = None,
    ):
        """Crawl and save URLs by repeatedly clicking the load button.

        This method opens the website, clicks the specified button multiple times
        to load more content, extracts URLs from newly appeared elements after each
        click, and saves them to a JSONL file. Already extracted URLs are
        automatically skipped.

        Args:
            click_time (int, optional): Number of times to click the load button.
                If None, uses self.click_time. Defaults to None.

        Returns:
            None: URLs are saved to the file specified by url_path, and the
                WebDriver is closed after completion.

        Note:
            - After each click, extracts URLs from all currently visible elements
              matching block1.
            - Uses JavaScript click (execute_script) as primary method, with
              standard click as fallback.
            - If clicking fails (button disabled, disappeared, or limit reached),
              logs a warning and continues to the next iteration.
            - Waits sleep_time seconds after each click for content to load.
            - A progress bar displays the clicking progress.
            - Automatically closes the browser driver when finished.
            - Handles both absolute and relative URLs, converting relative URLs
              to absolute ones when necessary.
        """
        self.browse_website()
        n = 0
        click_time = click_time if click_time is not None else self.click_time

        is_url_path = os.path.isfile(self.url_path)
        if is_url_path:
            url_list = pd.read_json(self.url_path, lines=True, engine="pyarrow", dtype_backend="pyarrow")["link"].to_list()
        else:
            url_list = None

        with tqdm(total=click_time, desc="Clicking") as pbar:
            while n < click_time:
                elements = self.driver.find_elements(By.CLASS_NAME, self.block1[1])

                for item in elements:
                    item = item.find_element(By.TAG_NAME, "a")
                    url = item.get_attribute("href")
                    if self.root_path:
                        if self.root_path[-1] == url[0] == "/":
                            self.root_path = self.root_path[:-1]
                        elif (self.root_path[-1] != "/") and (url[0] != "/"):
                            self.root_path = self.root_path + "/"
                        elif ("http" in self.root_path) and ("http" in url):
                            self.root_path = ""
                        url = self.root_path + url
                    else:
                        if "http" not in url:
                            root_path = get_root_path(self.prefix)
                            if url[0] == "/":
                                url = root_path + url
                            else:
                                url = root_path + "/" + url
                    if url_list and (url in url_list):
                        continue 
                    dictt = {"link": url}

                    with open(self.url_path, "ab") as file:
                        file.write(orjson.dumps(dictt, option=orjson.OPT_NON_STR_KEYS) + b"\n")

                button = self.driver.find_element(By.CLASS_NAME, self.block2[1])
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                except:
                    try:
                        button.click()
                    except:
                        logger.warning("Reach click limit or finish clicking.")
                n += 1
                if self.sleep_time:
                    time.sleep(self.sleep_time)
                pbar.update(1)

        self.driver.quit()

    def check_link_result(
        self,
        click_time: int = 5,
    ):
        """Check and print extracted URLs from multiple button clicks.

        This method opens the website, clicks the button multiple times to load
        more content, extracts all URLs that appear after each click, and prints
        the complete list to stdout. Useful for testing and verifying that URL
        extraction is working correctly.

        Args:
            click_time (int, optional): Number of times to click the load button
                for testing. Defaults to 5.

        Returns:
            None: Prints a list of all extracted URLs to stdout.

        Note:
            - Performs the clicking and extraction process but does not save
              URLs to file.
            - Does not check for or skip duplicate URLs.
            - Uses the same click mechanism as crawl_link (JavaScript click
              with standard click fallback).
            - Waits sleep_time seconds after each click.
            - A progress bar displays the clicking progress.
        """
        link_list = []
        self.browse_website()
        n = 0
        click_time = click_time if click_time is not None else self.click_time

        with tqdm(total=click_time, desc="Clicking") as pbar:
            while n < click_time:
                elements = self.driver.find_elements(By.CLASS_NAME, self.block1[1])

                for item in elements:
                    item = item.find_element(By.TAG_NAME, "a")
                    url = item.get_attribute("href")
                    if self.root_path:
                        if self.root_path[-1] == url[0] == "/":
                            self.root_path = self.root_path[:-1]
                        elif (self.root_path[-1] != "/") and (url[0] != "/"):
                            self.root_path = self.root_path + "/"
                        elif ("http" in self.root_path) and ("http" in url):
                            self.root_path = ""
                        url = self.root_path + url
                    link_list.append(url)

                button = self.driver.find_element(By.CLASS_NAME, self.block2[1])
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                except:
                    try:
                        button.click()
                    except:
                        logger.warning("Reach click limit or finish clicking.")
                n += 1
                if self.sleep_time:
                    time.sleep(self.sleep_time)
                pbar.update(1)
        print(link_list)