import requests
import uuid
from pathlib import Path
import orjson
from typing import Optional
from loguru import logger
from .scheduler import Scheduler


class Controller:
    """Controller class for managing the web crawling scheduler and tasks.

    This class provides an interface to control the crawling scheduler server,
    including launching, shutting down, checking status, and managing scheduled tasks.
    It supports adding, pausing, resuming, and removing scheduled crawling jobs
    defined in the configuration files.

    Args:
        host (Optional[str]): The host address of the scheduler server. Defaults to "127.0.0.1".
        port (Optional[int]): The port number of the scheduler server. Defaults to 5000.
        config_dir (Optional[str]): Directory to store configuration files. Defaults to "config".
        website_config_path (Optional[str]): Path to the website configuration file. Optional.
        log_path (Optional[str]): File path to save log output. Optional.
    """
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        config_dir: Optional[str] = None,
        website_config_path: Optional[str] = None,
        log_path: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.host = host if host is not None else "127.0.0.1"
        self.port = port if port is not None else 5000
        self.log_path = log_path
        self.root_path = "http://{}:{}".format(self.host, str(self.port))
        if config_dir is not None:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        if log_path is not None:
            logger.add(log_path, level="INFO", encoding="utf-8", enqueue=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.task_config_path = self.config_dir / "tasks.json"
        self.website_config_path = website_config_path

    def launch_scheduler(self):
        """Launch the crawling scheduler.

        This method initializes and starts the scheduler service,
        allowing background crawling tasks to be executed according to the defined schedule.

        Returns:
            None
        """
        self.scheduler = Scheduler(
            config_dir = str(self.config_dir),
            website_config_path = self.website_config_path,
            host = self.host,
            port = self.port,
            log_path=self.log_path
        )
        self.scheduler.run()

    def shutdown_scheduler(self):
        """Shut down the running scheduler.

        Sends a shutdown request to the scheduler server API.

        Returns:
            tuple[int, str] or None: A tuple containing the response status code and message text.
                Returns None if the connection fails.
        """
        api = self.root_path + "/shutdown"
        try:
            res = requests.post(api)
            return (res.status_code, res.text)
        except requests.exceptions.ConnectionError as e:
            logger.info("The scheduler has been shut down due to connection error.")

    def check_status(self):
        """Check the running status of the scheduler.

        Sends a GET request to the scheduler root endpoint to verify
        if the scheduler server is active.

        Returns:
            Union[tuple[int, str], str]: A tuple of HTTP status code and message if successful,
            otherwise a failure message string.
        """
        api = self.root_path
        try:
            res = requests.get(api)
            msg = "message: {}".format(res.text)
            return (res.status_code, msg)
        except:
            return "Failed to retrieve the status of the scheduler server."

    def retrieve_task_list(self):
        """Retrieve all registered tasks from the scheduler.

        Fetches a list of all scheduled tasks currently managed by the scheduler.

        Returns:
            Union[tuple[int, dict], str]: A tuple containing the HTTP status code
            and the JSON response (task list) if successful, or an error message string otherwise.
        """
        api = self.root_path + "/tasks"
        try:
            res = requests.get(api)
            return (res.status_code, res.json())
        except:
            message = "Something went wromg when retreiving the task list."
            logger.error(message)
            return message

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
        """Add a new crawling task to the scheduler.

        This function creates a new task configuration and sends it to the scheduler
        to be executed periodically based on the provided cron parameters.

        Args:
            task_type (str): Type of the task. Must be either `"update_all"` or `"by_idx"`.
            task_name (Optional[str]): Name of the task. Defaults to "update_all_task" or "by_idx_task".
            update_pages (Optional[int]): Number of pages to update in update mode. Optional.
            save_dir (Optional[str]): Directory to save the crawled data. Optional.
            start_idx (Optional[int]): Starting index in the website configuration. Defaults to 0.
            idx (Optional[int]): Specific website index for `"by_idx"` task type. Defaults to 0.
            cron_params (dict): Cron trigger parameters for scheduling. See:
                https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
            send_notification (Optional[bool]): Whether to send email notification after task completion.
            app_password (Optional[str]): Application-specific password for the sender email.
            sender_email (Optional[str]): Sender email address. Optional.
            recipient_email (Optional[str]): Recipient email address. Optional.

        Returns:
            Union[tuple[int, dict], None]: A tuple with the HTTP status code and JSON response if successful,
            or None if the scheduler request fails.

        Raises:
            ValueError: If `task_type` is not one of `"update_all"` or `"by_idx"`.
        """
        # For legal cron_params arguments, reference https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html.
        task_params = {}
        if task_type == "update_all":
            task_name = task_name if task_name is not None else "update_all_task"
            if update_pages is None:
                logger.warning("Scheduling updating task but update_pages argument is not assigned. Specifying it to 10 by default.")
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
        with open(self.task_config_path, "ab") as f:
            f.write(orjson.dumps(task_config, option=orjson.OPT_NON_STR_KEYS) + b"\n")

        api = self.root_path + "/start_task"
        data = {"task_id": task_id}
        try:
            res = requests.post(api, json=data)
            return (res.status_code, res.json())
        except:
            logger.error("Failed to add task into scheduler.")

    def start_task_from_config(
        self,
        task_id: str
    ):
        """Start a task from an existing task configuration file.

        Args:
            task_id (str): Unique identifier of the task to start.

        Returns:
            Union[tuple[int, dict], None]: A tuple with HTTP status code and JSON response,
            or None if the request fails.
        """
        api = self.root_path + "/start_task"
        data = {"task_id": task_id}
        try:
            res = requests.post(api, json=data)
            return (res.status_code, res.json())
        except:
            logger.error("Failed to add task with task_id {} into scheduler.".format(task_id))

    def pause_task(
        self,
        task_id: str
    ):
        """Pause a running task.

        Args:
            task_id (str): The unique task identifier to pause.

        Returns:
            Union[tuple[int, dict], None]: A tuple containing HTTP status code and JSON response,
            or None if the request fails.
        """
        api = self.root_path + "/pause"
        data = {"task_id": task_id}
        try:
            res = requests.post(api, json=data)
            return (res.status_code, res.json())
        except:
            logger.error("Failed to pause task with task_id: {}".format(task_id))

    def resume_task(
        self,
        task_id: str
    ):
        """Resume a paused task.

        Args:
            task_id (str): The unique task identifier to resume.

        Returns:
            Union[tuple[int, dict], None]: A tuple containing HTTP status code and JSON response,
            or None if the request fails.
        """
        api = self.root_path + "/resume"
        data = {"task_id": task_id}
        try:
            res = requests.post(api, json=data)
            return (res.status_code, res.json())
        except:
            logger.error("Failed to resume task with task_id: {}".format(task_id))

    def remove_task(
        self,
        task_id: str
    ):
        """Remove a task from the scheduler.

        Args:
            task_id (str): The unique task identifier to remove.

        Returns:
            Union[tuple[int, dict], None]: A tuple containing HTTP status code and JSON response,
            or None if the request fails.
        """
        api = self.root_path + "/remove"
        data = {"task_id": task_id}
        try:
            res = requests.post(api, json=data)
            return (res.status_code, res.json())
        except:
            logger.error("Failed to remove task with task_id: {}".format(task_id))