from musubi.agent import GeneralAgent
from musubi.agent.actions import (
    domain_analyze,
    implementation_analyze,
    update_all,
    update_by_idx,
    upload_data_folder,
    del_web_config_by_idx
)


general_actions = [domain_analyze, implementation_analyze, update_all, update_by_idx, upload_data_folder, del_web_config_by_idx]
general_agent = GeneralAgent(
    actions=general_actions,
    model_source="openai"
)

prompt = "Check how many websites I have scraped already."
general_agent.execute(prompt)