from apscheduler.schedulers.background import BackgroundScheduler
from ..pipeline import Pipeline
from .notification import Notify
from typing import Optional
import os


class CrawlScheduler:
    """
    Periodically crawl certain website depend on idx.
    """
    def __init__(
        self,
        send_notification: bool = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
    ):
        if send_notification:
            if app_password is not None:
                self.app_password = app_password
            elif os.environ.get("musubi_app_password"):
                self.app_password = os.environ.get("musubi_app_password")
            else:
                raise ValueError("To make scheduler send notification, please set app_password.")
            self.notify = Notify(
                app_password=self.app_password,
                sender_email=sender_email,
                recipient_email=recipient_email
            )
    
    def start_job(
        self,
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        idx: Optional[int] = None,
        upgrade_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: str = None,

    ):
        ...


