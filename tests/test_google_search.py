from ..musubi.agent.tools import google_search


def test_google_search(
    query: str = "The New York Times"
):
    url, root_path = google_search(query=query)
    print(url)
    print(root_path)