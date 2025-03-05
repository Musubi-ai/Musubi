import requests
from typing import Optional

from .scheduler import Scheduler
from .tasks import Task


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
    
    def launch_scheduler(
        self
    ):
        self.scheduler = Scheduler(
            host = self.host,
            port = self.port,
            debug = self.debug
        )
        self.scheduler.run()

    def shutdown_scheduler(
        self,
    ):
        api = self.root_path + "/shutdown"
        try:
            requests.post(api)
        except requests.exceptions.ConnectionError as e:
            print("The scheduler has been shut down.")

    def retrieve_task_list(
        self,
    ):
        api = self.root_path + "/tasks"
        try:
            res = requests.get(api)
            return res
        except:
            print("Something went wromg when retreiving the task list.")