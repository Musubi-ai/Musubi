from apscheduler.schedulers.background import BackgroundScheduler
from ..pipeline import Pipeline
from .notification import Notify
from ..utils.env import create_env_file
from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv, set_key
from flask import Flask
import pandas as pd

load_dotenv()

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()
active_tasks = {}


class Scheduler:
    def __init__(
        self,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        if send_notification:
            if app_password is not None:
                if os.getenv("GOOGLE_APP_PASSWORD") != app_password:
                    env_path = create_env_file()
                    set_key(env_path, key_to_set="GOOGLE_APP_PASSWORD", value_to_set=app_password)
                self.app_password = app_password
            elif os.getenv("GOOGLE_APP_PASSWORD"):
                self.app_password = os.getenv("GOOGLE_APP_PASSWORD")
            else:
                raise ValueError("To let scheduler send notification, please set app_password.")
            self.notify = Notify(
                app_password=self.app_password,
                sender_email=sender_email,
                recipient_email=recipient_email
            )

        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / "tasks.json"

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = True
    ):
        if host is None:
            host = "127.0.0.1"
        if port is None:
            port = 5000
        self.root_path = "http://{}:{}".format(host, str(port))
        app.run(host=host, port=port, debug=debug)


@app.route("/")
def print_hello():
    return "Scheduler server is running."

@app.route("/tasks", methods=["GET"])
def retrieve_task_list():
    task_list = []
    for task_id, task_name in active_tasks.items():
        task = scheduler.get_job(task_id)
        status = "pausing" if task.next_run_time is None else "operating"
        task_list.append({"ID": task_id, "Name": task_name, "Status": status})
        print(f"  - ID: {task_id}, Name: {task_name}, Status: {status}")
    task_status_df = pd.DataFrame(task_list)
    return task_status_df

@app.route("/add/<path:config_dir>/<task_id>", methods=["POST"])
def add_task(
    task_id: str,
    config_dir: str = "config"
):
    website_config_path = Path(config_dir) / "websites.json"
    pipeline = Pipeline(website_config_path)
    tasks_path = Path(config_dir) / "tasks.json"
    tasks_path.touch(mode=0o600, exist_ok=True)

    task_df = pd.read_json(tasks_path, lines=True)
    task_config = task_df[task_df["task_id"]==task_id]
    assert len(task_config) != 0, "Cannot find the specified task with task_id: {}".format(task_id)
    assert len(task_config) == 1, "Detect multiple tasks sharing the same task id."
    task_data = task_config.iloc[0].to_dict()
    if task_data["task_type"] == "upgrade_all":
        scheduler.add_job(
            pipeline.start_all,
            'cron', 
            id=task_id, 
            kwargs=task_data["task_params"],
            **task_data["cron_params"]
        )
        active_tasks[task_id] = task_data["task_name"]
    elif task_data["task_type"] == "by_idx":
        scheduler.add_job(
            pipeline.start_by_idx,
            'cron', 
            id=task_id, 
            kwargs=task_data["task_params"],
            **task_data["cron_params"]
        )
        active_tasks[task_id] = task_data["task_name"]
    else:
        raise ValueError("The task type of specified task should be one of 'upgrade_all' or 'by_idx' but got {}".format(task_data["task_type"]))

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