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
    def __init__(
        self,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None
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

        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / "tasks.json"
        self.website_config_path = self.config_dir / "websites.json"
        self.pipeline = Pipeline(website_config_path=self.website_config_path)

    def update_all(
        self,
        task_name: str = "update_all_task",
        start_idx: Optional[int] = 0,
        update_pages: int = 10,
        save_dir: Optional[str] = None
    ):
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