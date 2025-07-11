from musubi.agent import PipelineAgent
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info,
    final_answer
)


actions = [google_search, analyze_website, get_container, get_page_info, final_answer]
pipeline_agent = PipelineAgent(
    actions=actions,
    model_source="openai"
)

prompt = "Help me scrape all pages of articles from the 'Fiction and Poetry' category on Literary Hub."
pipeline_agent.execute(prompt)