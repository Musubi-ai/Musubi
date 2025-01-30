from ..musubi import Pipeline


def test_pipeline():
    pipeline = Pipeline()
    config_dict = {"dir": "test", 
    "name": "test", 
    "class_": "中文", 
    "prefix": "https://www.wazaiii.com/category?tag=17&ntype=&pages=", 
    "suffix": None, 
    "root_path": None, 
    "pages": 5, 
    "block1": ["div", "entry-image"], 
    "block2": None, 
    "type": "scan", 
    "async_": True}

    pipeline.pipeline(**config_dict)


def test_pipeline2():
    pipeline = Pipeline()
    config_dict = {"dir": "test2", 
    "name": "test2", 
    "class_": "中文", 
    "prefix": "https://www.twreporter.org/topics?page=", 
    "suffix": None, 
    "root_path": "https://www.twreporter.org/", 
    "pages": 5, 
    "block1": ["a", "topic-item__StyledLink-sc-1tffa4f-0 gvBqQB"], 
    "block2": None, 
    "type": "scan", 
    "async_": True}

    pipeline.pipeline(**config_dict)