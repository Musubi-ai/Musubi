import requests
import uuid
from pathlib import Path
import json
from typing import Optional
from rich.console import Console
from .scheduler import Scheduler


console = Console()


class Controller:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = False,
        config_dir: Optional[str] = None,
        website_config_path: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.host = host if host is not None else "127.0.0.1"
        self.port = port if port is not None else 5000
        self.root_path = "http://{}:{}".format(self.host, str(self.port))
        if config_dir is not None:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.task_config_path = self.config_dir / "tasks.json"
        self.website_config_path = website_config_path

    def launch_scheduler(self):
        self.scheduler = Scheduler(
            config_dir = str(self.config_dir),
            website_config_path = self.website_config_path,
            host = self.host,
            port = self.port,
            debug = self.debug
        )
        self.scheduler.run()

    def shutdown_scheduler(self):
        api = self.root_path + "/shutdown"
        try:
            requests.post(api)
        except requests.exceptions.ConnectionError as e:
            console.log("The scheduler has been shut down.", style="red1")

    def check_status(self):
        api = self.root_path
        try:
            res = requests.get(api)
            msg = "status code: {}, message: {}".format(res.status_code, res.text)
            return (res.status_code, msg)
        except:
            return "Failed to retrieve the status of the scheduler server."

    def retrieve_task_list(self):
        api = self.root_path + "/tasks"
        try:
            res = requests.get(api)
            console.log(res.content, style="green1")
            return res
        except:
            return "Something went wromg when retreiving the task list."

    def add_task(
        self,
        task_type: str,
        task_name: Optional[str] = None,
        update_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
        start_idx: Optional[int] = 0,
        idx: Optional[int] = 0,
        cron_params: dict = None,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None
    ):
        # For legal cron_params arguments, reference https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html.
        task_params = {}
        if task_type == "update_all":
            task_name = task_name if task_name is not None else "update_all_task"
            if update_pages is None:
                console.log("Scheduling updating task but update_pages argument is not assigned. Specifying it to 10 by default.", style="yellow1")
            update_pages = update_pages if update_pages is not None else 10
            task_params["task_name"] = task_name
            task_params["start_idx"] = start_idx
            task_params["update_pages"] = update_pages
            task_params["save_dir"] = save_dir
        elif task_type == "by_idx":
            task_name = task_name if task_name is not None else "by_idx_task"
            task_params["task_name"] = task_name
            task_params["idx"] = idx
            task_params["update_pages"] = update_pages
            task_params["save_dir"] = save_dir
        else:
            raise ValueError("The task type of specified task should be one of 'update_all' or 'by_idx' but got {}".format(task_type))
        
        if send_notification:
            contact_params = {
                "send_notification": True, 
                "app_password": app_password, 
                "sender_email": sender_email, 
                "recipient_email": recipient_email
            }
        else:
            contact_params = {"send_notification": False}
        
        task_id = str(uuid.uuid4())
        task_config = {
            "task_id": task_id,
            "task_type": task_type,
            "config_dir": str(self.config_dir),
            "task_params": task_params,
            "cron_params": cron_params,
            "contact_params": contact_params
        }
        
        with open(self.task_config_path, "a+", encoding="utf-8") as file:
            file.write(json.dumps(task_config, ensure_ascii=False) + "\n")

        api = self.root_path + "/task/{}".format(task_id)
        try:
            requests.post(api)
            console.log("Task with task_id '{}' has been added into config file and started.".format(task_id), style="green1")
        except:
            console.log("Failed to add task into scheduler.", style="red1")

    def start_task_from_config(
        self,
        task_id: str
    ):
        api = self.root_path + "/task/{}".format(task_id)
        try:
            requests.post(api)
            console.log("Task with task_id '{}' has started".format(task_id), style="green1")
        except:
            console.log("Failed to add task with task_id {} into scheduler.".format(task_id), style="red1")

    def pause_task(
        self,
        task_id: str
    ):
        api = self.root_path + "/pause/{}".format(task_id)
        try:
            requests.post(api)
            console.log("Task with task_id '{}' has been paused".format(task_id), style="green1")
        except:
            console.log("Failed to pause task with task_id: {}".format(task_id), style="red1")

    def resume_task(
        self,
        task_id: str
    ):
        api = self.root_path + "/resume/{}".format(task_id)
        try:
            requests.post(api)
            console.log("Task with task_id '{}' has been resumed".format(task_id), style="green1")
        except:
            console.log("Failed to resume task with task_id: {}".format(task_id), style="red1")

    def remove_task(
        self,
        task_id: str
    ):
        api = self.root_path + "/remove/{}".format(task_id)
        try:
            requests.post(api)
            console.log("Task with task_id '{}' has been removed".format(task_id), style="green1")
        except:
            console.log("Failed to remove task with task_id: {}".format(task_id), style="red1")