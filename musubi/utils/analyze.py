import pandas as pd
import os
from pathlib import Path
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"


class ConfigAnalyzer:
    """A analyzer for examining website configuration statistics and patterns.

    This class provides analysis tools for website configuration files, including
    domain statistics and implementation method distribution. It reads configuration
    data from a JSON file and generates summary statistics.

    Args:
        website_config_path (str or Path, optional): Path to the website configuration
            JSON file. If None, defaults to 'config/websites.json'. Defaults to None.

    Note:
        - The configuration file is expected to be in JSONL (JSON Lines) format.
        - The DataFrame is loaded using pandas with the 'lines=True' parameter.
    """
    def __init__(
        self,
        website_config_path = None
    ):
        self.website_config_path = website_config_path if website_config_path is not None else Path("config") / "websites.json"
        self.df = pd.read_json(self.website_config_path, lines=True)

    def domain_analyze(self):
        """Analyze and return domain statistics from the configuration.

        This method counts the number of unique main domains and total sub-domains
        (individual website entries) in the configuration file.

        Returns:
            dict: A dictionary containing domain statistics with the following keys:
                - 'num_main_domain' (int): Number of unique main domains.
                - 'num_sub_domain' (int): Total number of sub-domains/website entries.
        """
        main_domain = self.df["dir_"].to_list()
        num_domains = len(set(main_domain))
        num_sub_domain = len(self.df)
        return {"num_main_domain": num_domains, "num_sub_domain": num_sub_domain}
    
    def implementation_analyze(self):
        """Analyze and return implementation method distribution statistics.

        This method counts how many websites use each type of crawler implementation
        (scan, scroll, onepage, click) and returns the distribution.

        Returns:
            dict: A dictionary containing implementation statistics with the following keys:
                - 'all_num' (int): Total number of website configurations.
                - 'scan' (int): Number of websites using the Scan implementation.
                - 'scroll' (int): Number of websites using the Scroll implementation.
                - 'onepage' (int): Number of websites using the OnePage implementation.
                - 'click' (int): Number of websites using the Click implementation.

        Note:
            - Implementation types are identified by the 'implementation' field in
              the configuration.
            - The four recognized implementation types correspond to different
              crawler classes: Scan (paginated), Scroll (infinite scroll),
              OnePage (single page), and Click (load more button).
        """
        type_class = ["scan", "scroll", "onepage", "click"]
        type_list = self.df["implementation"].to_list()
        all_num = len(type_list)
        type_dict = {"all_num": all_num}
        for item in type_class:
            num = type_list.count(item)
            type_dict[item] = num
        
        return type_dict


class WebsiteNavigationAnalyzer:
    """An analyzer for automatically detecting website navigation and content loading patterns.

    This class uses Selenium WebDriver to analyze how a website loads additional
    content and determines the appropriate crawler implementation type (click, scroll,
    scan, or onepage). It tests various navigation mechanisms including buttons,
    infinite scrolling, and pagination.

    Args:
        url (str): The URL of the website to analyze.

    Note:
        - The analyzer tests navigation patterns in priority order: buttons (click),
          scrolling (scroll), pagination (scan), then defaults to single page (onepage).
        - Requires Microsoft Edge WebDriver to be installed.
        - The browser runs in headless mode for automated analysis.
    """
    def __init__(self, url):
        self.url = url
        self.driver = None
        
    def setup_selenium(self):
        """Initialize the Selenium WebDriver with optimized settings.

        This method creates a headless Edge browser instance configured for
        automated website analysis. The driver is stored in self.driver.

        Returns:
            None: Sets self.driver with the initialized WebDriver instance.

        Note:
            - The browser runs in headless mode (no visible window).
            - Window size is set to 1920x1080 for consistent rendering.
            - GPU acceleration is disabled for better compatibility in headless mode.
        """
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Edge(options=options)
        
    def analyze_navigation_type(self):
        """Analyze and determine the website's navigation pattern.

        This method tests the website for various content loading mechanisms in
        priority order and returns the most appropriate crawler implementation type.
        The detection order is: clickable buttons, infinite scroll, pagination,
        then single page.

        Returns:
            str: The recommended crawler implementation type. One of:
                - 'click': Website uses clickable buttons (e.g., "Load More", "Next").
                - 'scroll': Website uses infinite scrolling to load content.
                - 'scan': Website uses traditional pagination links.
                - 'onepage': Website displays all content on a single page.

        Note:
            - The WebDriver is automatically closed after analysis, even if errors occur.
            - Waits 2 seconds after loading the page for initial content to render.
            - Tests are performed in priority order to select the most specific
              navigation type.
        """
        try:
            self.setup_selenium()
            self.driver.get(self.url)
            time.sleep(2)

            buttons = self.check_buttons()
            if buttons:
                return "click"

            is_scrollable = self.check_scroll()
            if is_scrollable:
                return "scroll"
            
            pagination = self.check_pagination()

            if pagination:
                return "scan"

            return "onepage"
            
        finally:
            if self.driver:
                self.driver.quit()

    def check_pagination(self):
        """Check if the website uses traditional pagination links.

        This method searches for common pagination elements such as page links,
        pagination classes, or page number indicators.

        Returns:
            bool: True if pagination elements are found, False otherwise.

        Note:
            - Searches for elements with 'page' in href attributes, 'pagination'
              class, or 'page-numbers' class.
            - Returns False if an error occurs during detection.
        """
        try:
            pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='page'], .pagination, .page-numbers")
            if pagination_elements:
                return True
        except:
            logger.error("Error happens when checking pagination.")
        return False
    
    def check_buttons(self):
        """Check if the website uses clickable buttons to load more content.

        This method searches for various button patterns commonly used for loading
        additional content, such as "Next", "Load More", "Read More" buttons in
        both English and Chinese. It tests up to 3 clickable buttons to verify
        they actually load new content.

        Returns:
            bool: True if functional content-loading buttons are found, False otherwise.

        Note:
            - Tests multiple button patterns including pagination buttons, load more
              buttons, and read more buttons.
            - Only considers buttons that are both displayed and enabled.
            - Verifies button functionality by clicking and checking if page content
              changes.
            - Tests up to 3 buttons per pattern to confirm functionality.
            - Waits 2 seconds after each click for content to load.
            - Supports both English and Chinese button text.
        """
        button_patterns = [
            "//button[contains(text(), '下一頁') or contains(text(), 'Next')]",
            "//button[contains(@class, 'page') and not(contains(@class, 'disabled'))]",
            "//a[contains(@class, 'page-link') and not(contains(@class, 'disabled'))]",

            "//div[contains(@class, 'pagination')]//button",
            "//nav[contains(@class, 'pagination')]//button",

            "//button[contains(text(), '閱讀更多') or contains(text(), 'Read More')]",
            
            "//button[contains(text(), '載入更多') or contains(text(), 'Load More')]",
            "//div[contains(@class, 'load-more')]//button"
        ]
        
        for pattern in button_patterns:
            try:
                elements = self.driver.find_elements(By.XPATH, pattern)
                if not elements:
                    continue
                
                clickable_elements = [
                    elem for elem in elements 
                    if elem.is_displayed() and elem.is_enabled()
                ]
                
                if clickable_elements:
                    initial_content = self.driver.page_source
                    
                    for elem in clickable_elements[:3]:
                        try:
                            elem.click()
                            time.sleep(2)
                            
                            new_content = self.driver.page_source
                            if new_content != initial_content:
                                return True
                        except Exception:
                            continue
            
            except Exception as e:
                logger.error(f"Error raised when checking button pattern: {str(e)}")
        
        return False
    
    def check_scroll(self):
        """Check if the website uses infinite scrolling to load more content.

        This method scrolls to the bottom of the page and checks if the page height
        increases, indicating that new content was dynamically loaded.

        Returns:
            bool: True if the page height increases after scrolling (infinite scroll
                detected), False otherwise.

        Note:
            - Scrolls to the absolute bottom of the page using JavaScript.
            - Waits 2 seconds after scrolling for content to load.
            - Compares page height before and after scrolling to detect new content.
        """
        initial_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        return new_height > initial_height


if __name__ == "__main__":
    analyze = ConfigAnalyzer()
    type_dict = analyze.type_analyze()
    print(type_dict)
