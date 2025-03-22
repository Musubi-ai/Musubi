from ..musubi.agent.actions.pipeline_tool_actions import get_container


urls = [
    "https://e-creative.media/archives/category/lifestyle/page/2",
    "https://news.homeplus.net.tw/localnews/11?page=2",
    "https://mydigitalexperiences.com/blog/",
    "https://www.onejapan.com.tw/blog",
    "https://www.twreporter.org/topics?page=1",
    "https://www.thenewslens.com/category/politics",
    "https://heho.com.tw/archives/category/health-care/research-report",
    "https://www.taiwan66.com.tw/channel/list/type/all-latest/0/tag/0/ln/zh/page/18#post-entry"
]

def test_get_container():
    block1_ans = []
    block2_ans = []
    for url in urls:
        block1, block2 = get_container(url)
        block1_ans.append(block1)
        block2_ans.append(block2)

    assert block1_ans == [
        ["h3", "jeg_post_title"],
        ["div", "inner"],
        ["h2", "entry-title"],
        ["div", "card mb-3 custom-hover"],
        ["a", "topic-item__StyledLink-sc-1tffa4f-0 gvBqQB"],
        ["h3", "item-title h5 mb-2"],
        ["h5", "post-title is-large"],
        ['a', 'basic-post__itemsub']
    ]

    assert block2_ans == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    ]