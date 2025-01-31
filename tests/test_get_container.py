from ..musubi.agent.tools import get_container


urls = [
    "https://e-creative.media/archives/category/lifestyle/page/2",
    "https://news.homeplus.net.tw/localnews/11?page=2",
    "https://mydigitalexperiences.com/blog/",
    "https://www.onejapan.com.tw/blog",
    "https://www.twreporter.org/topics?page=1",
    "https://www.thenewslens.com/category/politics",
    "https://heho.com.tw/archives/category/health-care/research-report"
]

def test_get_container():
    ans = []
    for url in urls:
        container = get_container(url)
        ans.append(container)

    assert ans == [
        ["h3", "jeg_post_title"],
        ["div", "inner"],
        ["h2", "entry-title"],
        ["div", "card mb-3 custom-hover"],
        ["a", "topic-item__StyledLink-sc-1tffa4f-0 gvBqQB"],
        ["h3", "item-title h5 mb-2"],
        ["h5", "post-title is-large"]
    ]