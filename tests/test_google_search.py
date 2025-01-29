from ..musubi.agent.tools import google_search


def test_google_search(
    query: str = "行政院 本院新聞"
):
    res = google_search(query=query, headless=True)
    print(res)