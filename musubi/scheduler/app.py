from apscheduler.schedulers.background import BackgroundScheduler
# from ..pipeline import Pipeline
from .notification import Notify
# from .params_retriever import get_cron_params, get_idx_task_params, get_upgrade_task_params
from ..utils.env import create_env_file
from pathlib import Path
import os
import uuid
import time
import json
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv, set_key
from flask import Flask, jsonify
import pandas as pd

load_dotenv()

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()
active_jobs = {"jobs": "a"}


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
        self.active_jobs = {}

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = False
    ):
        if host is None:
            host = "127.0.0.1"
        if port is None:
            port = 5000
        self.root_path = "http://{}:{}".format(host, str(port))
        app.run(host=host, port=port, debug=debug)


@app.route("/")
def print_hello():
    return "Hello!!!!!"

@app.route("/tasks", methods=["GET"])
def retrieve_task_list():
    return active_jobs

@app.route("/add", methods=["POST"])
def add_tasks():
    ...