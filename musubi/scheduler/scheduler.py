from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import os
import sys
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn
import pandas as pd
from dataclasses import dataclass, field
from loguru import logger
from .tasks import Task
from .dataformat import (
    SchedulerInfo,
    TasksResponse,
    StartTaskResponse,
    GeneralRequest,
    GeneralResponse
)


logger.add(sys.stderr, level="ERROR")

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.start()
active_tasks = {}


scheduler_info = SchedulerInfo(active_tasks={})


class Scheduler:
    def __init__(
        self,
        config_dir: Optional[str] = None,
        website_config_path: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        log_path: Optional[str] = None
    ):
        self.host = host
        self.port = port
        if config_dir is not None:
            scheduler_info.config_dir = config_dir
        if website_config_path is not None:
            scheduler_info.website_config_path = website_config_path
        if log_path is not None:
            logger.add(log_path, level="INFO", encoding="utf-8", enqueue=True) 

    def run(self):
        if self.host is None:
            self.host = "127.0.0.1"
        if self.port is None:
            self.port = 5000
        logger.info("Start scheduler.")
        uvicorn.run(app, host=self.host, port=self.port)


@app.get("/")
async def check():
    return PlainTextResponse("Scheduler server is running.")

@app.get("/tasks")
async def retrieve_task_list():
    task_response = TasksResponse()
    try:
        for task_id, task_name in active_tasks.items():
            task = scheduler.get_job(task_id)
            status = "pausing" if task.next_run_time is None else "operating"
            task_response.tasks.append({"ID": task_id, "Name": task_name, "Status": status})
        if len(task_response.tasks) == 0:
            task_response.message = "No scheduled task."
            return ORJSONResponse(task_response)
        for item in task_response.tasks:
            logger.info(f"  - ID: {item['ID']}, Name: {item['Name']}, Status: {item['Status']}")
            task_response.message = "Retrived successfully."
            logger.info(task_response.message)
    except Exception:
        task_response.message = "Failed to retrieve scheduled tasks."
        logger.error(task_response.message)
    return ORJSONResponse(task_response)

@app.post("/start_task")
async def start_task(request_data: GeneralRequest):
    tasks_path = Path(scheduler_info.config_dir) / "tasks.json"
    tasks_path.touch(mode=0o600, exist_ok=True)
    response_data = StartTaskResponse()

    try:
        task_df = pd.read_json(tasks_path, lines=True)
        task_config = task_df[task_df["task_id"]==request_data.task_id]
        if len(task_config) == 0:
            response_data.message = "Cannot find the specified task with task_id: {}".format(request_data.task_id)
            logger.warning(response_data.message)
            return ORJSONResponse(response_data)
        elif len(task_config) != 1:
            response_data.message = "Detect multiple tasks sharing the same task id."
            logger.warning(response_data.message)
            return ORJSONResponse(response_data)
        task_data = task_config.iloc[0].to_dict()
        task_init = Task(
            config_dir=scheduler_info.config_dir,
            website_config_path=scheduler_info.website_config_path,
            **task_data["contact_params"]
        )
        if task_data["task_type"] == "update_all":
            scheduler.add_job(
                task_init.update_all,
                'cron', 
                id=request_data.task_id, 
                kwargs=task_data["task_params"],
                **task_data["cron_params"]
            )
            active_tasks[request_data.task_id] = task_data["task_params"]["task_name"]
        elif task_data["task_type"] == "by_idx":
            scheduler.add_job(
                task_init.by_idx,
                'cron', 
                id=request_data.task_id, 
                kwargs=task_data["task_params"],
                **task_data["cron_params"]
            )
            active_tasks[request_data.task_id] = task_data["task_params"]["task_name"]
        else:
            response_data.message = "The task type of specified task should be one of 'update_all' or 'by_idx' but got {}".format(task_data["task_type"])
            logger.error(response_data.message)
            return ORJSONResponse(response_data)
        response_data.task_data = task_data
        response_data.message = "Start task {} succeffsully.".format(request_data.task_id)
        logger.info(response_data.message)
        return ORJSONResponse(response_data)
    except Exception:
        response_data.message = "Failed to start task with task_id: {}".format(request_data.task_id)
        logger.error(response_data.message)
        return ORJSONResponse(response_data)

@app.post("/pause")
async def pause_task(request_data: GeneralRequest):
    response_data = GeneralResponse()
    try:
        if request_data.task_id in active_tasks:
            scheduler.pause_job(request_data.task_id)
            response_data.message = "Pause task '{}'.".format(active_tasks[request_data.task_id])
            logger.info(response_data.message)
        else:
            response_data.message = "Cannot find the task having ID {}!".format(request_data.task_id)
            logger.warning(response_data.message)
        return ORJSONResponse(response_data)
    except Exception:
        response_data.message = "Failed to pause task."
        logger.error(response_data.message)
        return ORJSONResponse(response_data)

@app.post("/resume")
async def resume_task(request_data: GeneralRequest):
    response_data = GeneralResponse()
    try:
        if request_data.task_id in active_tasks:
            scheduler.resume_job(request_data.task_id)
            response_data.message = "Task '{}' has been resumed.".format(active_tasks[request_data.task_id])
            logger.info(response_data.message)
        else:
            response_data.message = "Cannot find task ID!"
            logger.warning(response_data.message)
        return ORJSONResponse(response_data)
    except Exception:
        response_data.message = "Failed to resume task with task_id: {}".format(request_data.task_id)
        logger.error(response_data.message)
        return ORJSONResponse(response_data)

@app.post("/remove")
def remove_task(request_data: GeneralRequest):
    response_data = GeneralResponse()
    try:
        if request_data.task_id in active_tasks:
            scheduler.remove_job(request_data.task_id)
            response_data.message = "Task '{}' has been removed from scheduler.".format(active_tasks[request_data.task_id])
            logger.info(response_data.message)
        else:
            response_data.message = "Cannot find task with task_id {} in scheduler!".format(request_data.task_id)
            logger.warning(response_data.message)
        return ORJSONResponse(response_data)
    except Exception:
        response_data.message = "Failed to remove task with task_id: {}".format(request_data.task_id)
        logger.error(response_data.message)
        return ORJSONResponse(response_data)

@app.post("/shutdown")
async def shutdown_scheduler():
    os._exit(0)
    message = "The scheduler has been shut down."
    logger.info(message)
    return PlainTextResponse(message)