from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import os
from typing import Optional
from flask import Flask
import pandas as pd
from .tasks import Task


app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()
active_tasks = {}


class Scheduler:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = True,
        config_dir: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.debug = debug


    def run(self):
        if self.host is None:
            self.host = "127.0.0.1"
        if self.port is None:
            self.port = 5000
        app.run(host=self.host, port=self.port, debug=self.debug)


@app.route("/", methods=["GET"])
def check():
    return "Scheduler server is running."

@app.route("/tasks", methods=["GET"])
def retrieve_task_list():
    task_list = []
    for task_id, task_name in active_tasks.items():
        task = scheduler.get_job(task_id)
        status = "pausing" if task.next_run_time is None else "operating"
        task_list.append({"ID": task_id, "Name": task_name, "Status": status})
    if len(task_list) == 0:
        msg = "No scheduled task."
        print(msg)
        return msg
    for item in task_list:
        print(f"  - ID: {item["ID"]}, Name: {item["Name"]}, Status: {item["Status"]}")
    return task_list

@app.route("/<string:task_id>", methods=["POST"])
def start_task(
    task_id: str
):
    tasks_path = Path("config") / "tasks.json"
    tasks_path.touch(mode=0o600, exist_ok=True)

    task_df = pd.read_json(tasks_path, lines=True)
    task_config = task_df[task_df["task_id"]==task_id]
    assert len(task_config) != 0, "Cannot find the specified task with task_id: {}".format(task_id)
    assert len(task_config) == 1, "Detect multiple tasks sharing the same task id."
    task_data = task_config.iloc[0].to_dict()
    task_init = Task(config_dir="config", **task_data["contact_params"])
    if task_data["task_type"] == "update_all":
        scheduler.add_job(
            task_init.update_all,
            'cron', 
            id=task_id, 
            kwargs=task_data["task_params"],
            **task_data["cron_params"]
        )
        active_tasks[task_id] = task_data["task_params"]["task_name"]
    elif task_data["task_type"] == "by_idx":
        scheduler.add_job(
            task_init.by_idx,
            'cron', 
            id=task_id, 
            kwargs=task_data["task_params"],
            **task_data["cron_params"]
        )
        active_tasks[task_id] = task_data["task_params"]["task_name"]
    else:
        raise ValueError("The task type of specified task should be one of 'update_all' or 'by_idx' but got {}".format(task_data["task_type"]))
    return task_data

@app.route("/pause/<task_id>", methods=["POST"])
def pause_task(task_id: str):
    if task_id in active_tasks:
        scheduler.pause_job(task_id)
        print(f"Pause task '{active_tasks[task_id]}'.")
    else:
        print("Cannot find the task having ID {}!".format(task_id))

@app.route("/resume/<task_id>", methods=["POST"])
def resume_task(task_id: str):
    if task_id in active_tasks:
        scheduler.resume_job(task_id)
        print(f"Task '{active_tasks[task_id]}' has been resumed.")
    else:
        print("Cannot find task ID!")

@app.route("/shutdown", methods=["POST"])
def shutdown_scheduler():
    os._exit(0)
    return "Shut down"