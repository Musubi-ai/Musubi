import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class ConfigAnalyzer:
    def __init__(
        self,
        website_config_path = Path("config") / "websites.json"
    ):
        self.website_config_path = website_config_path
        self.df = pd.read_json(self.website_config_path, lines=True)

    def domain_analyze(self):
        main_domain = self.df["dir"].to_list()
        num_domains = len(set(main_domain))
        num_sub_domain = len(self.df)
        return {"num_main_domain": num_domains, "num_sub_domain": num_sub_domain}
    
    def type_analyze(self):
        type_class = ["scan", "scroll", "onepage", "click"]
        type_list = self.df["type"].to_list()
        all_num = len(type_list)
        type_dict = {"all_num": all_num}
        for item in type_class:
            num = type_list.count(item)
            type_dict[item] = num
        
        return type_dict


class WebsiteNavigationAnalyzer:
    def __init__(self, url):
        self.url = url
        self.driver = None
        
    def setup_selenium(self):
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Edge(options=options)
        
    def analyze_navigation_type(self):
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
        try:
            pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='page'], .pagination, .page-numbers")
            if pagination_elements:
                return True
        except:
            print("Error happens when checking pagination.")
        return False
    
    def check_buttons(self):
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
                print(f"Error raised when checking button pattern: {str(e)}")
        
        return False
    
    def check_scroll(self):
        initial_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        return new_height > initial_height


if __name__ == "__main__":
    analyze = ConfigAnalyzer()
    type_dict = analyze.type_analyze()
    print(type_dict)
