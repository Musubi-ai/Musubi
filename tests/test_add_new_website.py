from ..musubi.utils import add_new_website
from typing import Optional, List


def test_add_new_website(
    website_config_path: Optional[str] = None,
    idx: int = None,
    dir: str = "test",
    name: str = "test",
    class_: str = "test",
    prefix: str = "test",
    suffix: str = "test",
    root_path: str = "test",
    pages: int = 1,
    block1: list = ["test", "test"],
    block2: Optional[List] = None,
    img_txt_block: Optional[List] = None,
    type: str = "test",
    async_: bool = False,
    page_init_val: int = 1,
    multiplier: int = 1,
):
    add_new_website(
        website_config_path = website_config_path,
        idx = idx,
        dir = dir,
        name = name,
        class_ = class_,
        prefix = prefix,
        suffix = suffix,
        root_path = root_path,
        pages = pages,
        block1 = block1,
        block2 = block2,
        img_txt_block = img_txt_block,
        type = type,
        async_ = async_,
        page_init_val = page_init_val,
        multiplier = multiplier,
    )