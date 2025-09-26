from musubi.agent import PipelineAgent, GeneralAgent, SchedulerAgent, MusubiAgent
from musubi.agent.actions import (
    search_url,
    analyze_website,
    get_container,
    get_page_info,
    final_answer,
    domain_analyze,
    implementation_analyze,
    update_all,
    update_by_idx,
    upload_data_folder,
    del_web_config_by_idx,
    launch_scheduler,
    shutdown_scheduler,
    check_status,
    retrieve_task_list,
    add_task,
    start_task_from_config,
    pause_task,
    resume_task,
    remove_task
)


actions = [search_url, analyze_website, get_container, get_page_info, final_answer]
pipeline_agent = PipelineAgent(
    actions=actions,
    model_source="openai"
)


general_actions = [domain_analyze, implementation_analyze, update_all, update_by_idx, upload_data_folder, del_web_config_by_idx]
general_agent = GeneralAgent(
    actions=general_actions,
    model_source="openai"
)

scheduler_actions = [
    launch_scheduler, 
    shutdown_scheduler, 
    check_status, 
    retrieve_task_list, 
    add_task, 
    start_task_from_config, 
    pause_task, 
    resume_task, 
    remove_task
]
scheduler_agent = SchedulerAgent(
    actions=scheduler_actions,
    model_source="openai"
)

main_agent = MusubiAgent(candidates=[general_agent, pipeline_agent, scheduler_agent])
prompt = "Help me scrape all pages of articles from the 'Fiction and Poetry' category on Literary Hub."
main_agent.execute(prompt)