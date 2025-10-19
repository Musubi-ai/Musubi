import os
from datetime import datetime
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv, set_key
from .notification import Notify
from ..utils.env import create_env_file
from ..pipeline import Pipeline

load_dotenv()


class Task:
    """Represents a scheduled crawling task with optional email notifications.

    This class wraps the Musubi crawling pipeline and provides methods
    to execute scheduled tasks either for all websites or a specific
    website index. It can also send email notifications before and after
    the task execution.

    Args:
        send_notification (Optional[bool]): Whether to send email notifications.
            Defaults to False.
        app_password (Optional[str]): Gmail app password for sending notifications.
            Required if `send_notification` is True.
        sender_email (Optional[str]): Email address to send notifications from.
        recipient_email (Optional[str]): Email address to send notifications to.
            Defaults to `sender_email` if not provided.
        config_dir (Optional[str]): Directory to store task configuration files.
            Defaults to `"config"`.
        website_config_path (Optional[str]): Path to website configuration JSON file.
            Defaults to `"config/websites.json"`.
    """
    def __init__(
        self,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None,
        website_config_path: Optional[str] = None
    ):
        if send_notification:
            self.send_notification = send_notification
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

        if config_dir is not None:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / "tasks.json"
        if website_config_path  is not None:
            self.website_config_path = website_config_path
        else:
            self.website_config_path = self.config_dir / "websites.json"
        self.pipeline = Pipeline(website_config_path=self.website_config_path)

    def update_all(
        self,
        task_name: str = "update_all_task",
        start_idx: Optional[int] = 0,
        update_pages: int = 10,
        save_dir: Optional[str] = None
    ):
        """Execute a scheduled update task for all websites.

        Sends optional email notifications before and after executing the
        full update task using the Musubi pipeline.

        Args:
            task_name (str): Name of the task. Defaults to `"update_all_task"`.
            start_idx (Optional[int]): Starting index in the website configuration
                to begin crawling. Defaults to 0.
            update_pages (int): Number of pages to update per website. Defaults to 10.
            save_dir (Optional[str]): Directory to save extracted data. Optional.

        Returns:
            None
        """
        if self.send_notification:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled updating",
                body="Start scheduled task '{}' at {}".format(task_name, datetime.now())
            )

        self.pipeline.start_all(
            start_idx=start_idx,
            update_pages=update_pages,
            save_dir=save_dir
        )

        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Finished scheduled updating",
                body="Finished scheduled task '{}' at {}".format(task_name, datetime.now())
            )

    def by_idx(
        self,
        task_name: str = "by_idx_task",
        idx: Optional[int] = 0,
        update_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
    ):
        """Execute a scheduled task for a specific website by index.

        Sends optional email notifications before and after executing the
        crawling task for the website at the specified index using the
        Musubi pipeline.

        Args:
            task_name (str): Name of the task. Defaults to `"by_idx_task"`.
            idx (Optional[int]): Index of the website in the configuration.
                Defaults to 0.
            update_pages (Optional[int]): Number of pages to update. Optional.
            save_dir (Optional[str]): Directory to save extracted data. Optional.

        Returns:
            None
        """
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled crawling",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )
        
        self.pipeline.start_by_idx(
            idx=idx,
            update_pages=update_pages,
            save_dir=save_dir
        )

        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Finished scheduled crawling",
                body="Finished scheduled task {} at {}".format(task_name, datetime.now())
            )