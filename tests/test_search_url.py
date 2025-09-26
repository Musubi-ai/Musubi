from ..musubi.agent.actions.pipeline_tool_actions import search_url


def test_search_url(
    query: str = "The New York Times"
):
    url, root_path = search_url(query=query)
    print(url)
    print(root_path)