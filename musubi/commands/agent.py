import argparse
from ..agent import PipelineAgent, GeneralAgent, SchedulerAgent, MusubiAgent
from ..agent.actions import (
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


def agent_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("agent")
    else:
        parser = argparse.ArgumentParser("Musubi agent command")

    parser.add_argument(
        "--prompt", type=str, default=None, help="Google search api for searching.", required=True
    )
    parser.add_argument(
        "--model_source", type=str, default="openai", help="Google search api for searching."
    )
    parser.add_argument(
        "--api_key", type=str, default=None, help="Google search api for searching."
    )
    parser.add_argument(
        "--model_type", type=str, default=None, help="Google search api for searching."
    )
    if subparsers is not None:
        parser.set_defaults(func=agent_command)
    return parser


def agent_command(args):
    actions = [google_search, analyze_website, get_container, get_page_info, final_answer]
    pipeline_agent = PipelineAgent(
        actions=actions,
        model_source=args.model_source,
        api_key=args.api_key,
        model_type=args.model_type
    )

    general_actions = [domain_analyze, type_analyze, update_all, update_by_idx, upload_data_folder, del_web_config_by_idx]
    general_agent = GeneralAgent(
        actions=general_actions,
        model_source=args.model_source,
        api_key=args.api_key,
        model_type=args.model_type
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
        model_source=args.model_source,
        api_key=args.api_key,
        model_type=args.model_type
    )

    main_agent = MusubiAgent(candidates=[general_agent, pipeline_agent, scheduler_agent])
    main_agent.execute(args.prompt)