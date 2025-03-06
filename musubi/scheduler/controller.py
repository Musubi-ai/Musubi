import requests
import uuid
from pathlib import Path
import json
from typing import Optional
from .scheduler import Scheduler


class Controller:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = True
    ):
        self.host = host
        self.port = port
        self.debug = debug
        if self.host is None:
            self.host = "127.0.0.1"
        if self.port is None:
            self.port = 5000
        self.root_path = "http://{}:{}".format(self.host, str(self.port))

    def launch_scheduler(self):
        self.scheduler = Scheduler(
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
            print("The scheduler has been shut down.")

    def check_status(self):
        api = self.root_path
        try:
            res = requests.get(api)
            msg = "status code: {}, message: {}".format(res.status_code, res.text)
            print(msg)
        except:
            print("...")

    def retrieve_task_list(self):
        api = self.root_path + "/tasks"
        try:
            res = requests.get(api)
            return res
        except:
            print("Something went wromg when retreiving the task list.")

    def add_task(
        self,
        task_type: str,
        task_name: str,
        task_params: dict = None,
        cron_params: dict = None,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None,
    ):
        legal_task_type = ["update_all", "by_idx"]
        if task_type not in legal_task_type:
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
            "task_name": task_name,
            "task_type": task_type,
            "config_dir": config_dir,
            "task_params": task_params,
            "cron_params": cron_params,
            "contact_params": contact_params
        }
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.task_config_path = self.config_dir / "tasks.json"
        with open(self.task_config_path, "a+", encoding="utf-8") as file:
            file.write(json.dumps(task_config, ensure_ascii=False) + "\n")

        api = self.root_path + str(self.config_dir) + task_id
        try:
            requests.post(api)
        except:
            print("Failed to add task into scheduler.")