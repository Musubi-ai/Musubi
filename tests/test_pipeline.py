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


