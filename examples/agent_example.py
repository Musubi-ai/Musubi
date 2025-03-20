from musubi.agent import PipelineAgent, GeneralAgent, MusubiAgent
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info,
    final_answer,
    domain_analyze,
    type_analyze,
    update_all,
    update_by_idx,
    upload_data_folder,
    del_web_config_by_idx
)


actions = [google_search, analyze_website, get_container, get_page_info, final_answer]
pipeline_agent = PipelineAgent(
    actions=actions,
    model_source="openai"
)


general_actions = [domain_analyze, type_analyze, update_all, update_by_idx, upload_data_folder, del_web_config_by_idx]
general_agent = GeneralAgent(
    actions=general_actions,
    model_source="openai"
)


main_agent = MusubiAgent(candidates=[general_agent, pipeline_agent])
prompt = "幫我爬取Literary Hub上的Fiction and Poetry分類的所有頁數的文章" # 幫我爬取Literary Hub上的Fiction and Poetry分類的所有頁數的文章。 幫我分析website.json檔裡已經記錄下來的domain有多少？
main_agent.execute(prompt)