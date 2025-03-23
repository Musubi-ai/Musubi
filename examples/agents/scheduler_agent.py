from musubi.agent import SchedulerAgent
from musubi.agent.actions import (
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

prompt = "Shutdown the scheduler."
scheduler_agent.execute(prompt)