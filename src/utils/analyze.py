import pandas as pd


class WebAnalyzer:
    def __init__(
        self,
        websitelist_path = "websites.json"
    ):
        self.websitelist_path = websitelist_path
        self.df = pd.read_json(self.websitelist_path, lines=True)

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


if __name__ == "__main__":
    analyze = WebAnalyzer()
    type_dict = analyze.type_analyze()
    print(type_dict)
