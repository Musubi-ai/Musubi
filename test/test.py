from typing import List


class BaseCrawler:
    def __init__(
        self,
        prefix: str = None,
        prefix2: str = None,
        prefix3: str = None,
        pages: int = None,
        block1: List[str] = None,
        block2: List[str] = None,
        url_path: str = "aaaaaaaaaaaa",
        *args,
        **kwargs
    ):
        self.prefix = prefix
        self.prefix2 = prefix2
        self.prefix3 = prefix3
        self.pages = pages
        self.url_path = url_path
        self.block1 = block1
        self.block2 = block2
        


class Scan(BaseCrawler):
    def __init__(
        self,
        arg1: str = "",
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.arg1 = arg1
        self.arg2 = self.url_path
        self.arg2 = "ab"
        if len(self.url_path) > 3:
            print("yes")
        if self.pages == 1:
            self.pages_lst = [self.prefix]
        else:
            if self.prefix2:
                self.pages_lst = [self.prefix + str(i+1) + self.prefix2 for i in range(self.pages)]
            else:
                self.pages_lst = [self.prefix + str(i+1) for i in range(self.pages)]

        self.length = len(self.pages_lst)
        self.plural_a_tag = (self.block1[0] == "a") or (self.block2 and self.block2[0] == "a")


scan = Scan(
    arg1="lll",
    prefix="Httpss",
    pages=1,
    block1=["div", "Cute"],
    block2=["div", "Cute"]
)

print(scan.arg2)
print(scan.url_path)