from ..musubi.agent.actions import get_page_info


def test_get_page_info():
    url = r"https://lithub.com/category/fictionandpoetry/"
    root_path = r"https://lithub.com"
    res = get_page_info(
        url=url,
        root_path=root_path
    )
    assert res == ('https://lithub.com/category/fictionandpoetry/page/', '/', 170, 1, 1)
