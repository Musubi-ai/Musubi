from apscheduler.schedulers.background import BackgroundScheduler
from ..pipeline import Pipeline
from .notification import Notify
from .params_retriever import get_cron_params, get_idx_task_params, get_update_task_params
from ..utils.env import create_env_file
from typing import Optional
from pathlib import Path
import os
import uuid
import time
import json
from datetime import datetime
from abc import ABC, abstractmethod
from dotenv import load_dotenv, set_key
import pandas as pd

load_dotenv()


class BaseScheduler(ABC):
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

    @abstractmethod
    def launch_scheduler(self):
        ...
    

class IdxScheduler(BaseScheduler):
    """
    Periodically crawl certain website based on idx.
    """
    def __init__(
        self,
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        super().__init__(send_notification, app_password, sender_email, recipient_email, config_dir)

    def start_by_idx_task(
        self,
        website_config_path=None,
        idx: int = None,
        update_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
        task_name: str = None
    ):
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled crawling",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )

        pipe = Pipeline(website_config_path=website_config_path)
        pipe.start_by_idx(
            idx=idx,
            update_pages=update_pages,
            save_dir=save_dir
        )

        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Finished scheduled crawling",
                body="Finished scheduled task {} at {}".format(task_name, datetime.now())
            )
    
    def launch_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.start()

        active_jobs = {}

        try:
            while True:
                command = input("\nInput command ('add', 'pause', 'resume', 'list', 'exit'): ").strip().lower()
                
                if command == 'add':
                    try:
                        task_name = input("Task name: ").strip()
                        cron_params = get_cron_params()
                        task_params = get_idx_task_params()
                        task_params["task_name"] = task_name
                        # Generate unique task id by uuid4
                        task_id = str(uuid.uuid4())
                        
                        # Add task
                        scheduler.add_job(
                            self.start_by_idx_task, 
                            'cron', 
                            id=task_id, 
                            kwargs=task_params,
                            **cron_params
                        )
                        active_jobs[task_id] = task_name
                        print(f"Add task '{task_name}', ID: {task_id}")

                        task_config = {
                            "task_id": task_id, 
                            "cron_params": cron_params,
                            "task_params": task_params,
                            "task_type": "by_idx"
                        }
                        
                        with open(self.config_path, "a+", encoding="utf-8") as file:
                            file.write(json.dumps(task_config, ensure_ascii=False) + "\n")

                    except ValueError as e:
                        print(f"ValueError: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        continue
                
                elif command == 'pause':
                    task_id = input("Task ID: ").strip()
                    if task_id in active_jobs:
                        scheduler.pause_job(task_id)
                        print(f"Pause task '{active_jobs[task_id]}'.")
                    else:
                        print("Cannot find the task having ID {}!".format(task_id))
                
                elif command == 'resume':
                    task_id = input("Enter task ID: ").strip()
                    if task_id in active_jobs:
                        scheduler.resume_job(task_id)
                        print(f"Task '{active_jobs[task_id]}' has been resumed.")
                    else:
                        print("Cannot find task ID!")
                
                elif command == 'list':
                    print("Current task list：")
                    for task_id, task_name in active_jobs.items():
                        job = scheduler.get_job(task_id)
                        status = "pausing" if job.next_run_time is None else "operating"
                        print(f"  - ID: {task_id}, Name: {task_name}, Status: {status}")
                
                elif command == 'exit':
                    print("Shut downing Scheduler...")
                    scheduler.shutdown()
                    break
                
                else:
                    print("Invalid command. The command should be one of 'add', 'pause', 'resume', 'list', 'exit', but got {}".format(command))
                
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            print("Shut down scheduler.")


class UpgradeScheduler(BaseScheduler):
    def __init__(
        self, 
        send_notification: Optional[bool] = False,
        app_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        super().__init__(send_notification, app_password, sender_email, recipient_email, config_dir)

    def update_task(
        self,
        website_config_path=None,
        start_idx: Optional[int] = 0,
        update_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
        task_name: str = None
    ):
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled upgrading",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )

        pipe = Pipeline(website_config_path=website_config_path)
        pipe.start_all(
            start_idx=start_idx,
            update_pages=update_pages,
            save_dir=save_dir
        )

        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Finished scheduled upgrading",
                body="Finished scheduled task {} at {}".format(task_name, datetime.now())
            )

    def launch_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.start()

        active_jobs = {}

        try:
            while True:
                command = input("\nInput command ('add', 'pause', 'resume', 'list', 'exit'): ").strip().lower()
                
                if command == 'add':
                    try:
                        task_name = input("Task name: ").strip()
                        cron_params = get_cron_params()
                        task_params = get_update_task_params()
                        task_params["task_name"] = task_name
                        # Generate unique task id by uuid4
                        task_id = str(uuid.uuid4())
                        
                        # Add task
                        scheduler.add_job(
                            self.update_task, 
                            'cron', 
                            id=task_id, 
                            kwargs=task_params,
                            **cron_params
                        )
                        active_jobs[task_id] = task_name
                        print(f"Add task '{task_name}', ID: {task_id}")
                        task_config = {
                            "task_id": task_id, 
                            "cron_params": cron_params,
                            "task_params": task_params,
                            "task_type": "update_all"
                        }
                        
                        with open(self.config_path, "a+", encoding="utf-8") as file:
                            file.write(json.dumps(task_config, ensure_ascii=False) + "\n")

                    except ValueError as e:
                        print(f"ValueError: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        continue
                
                elif command == 'pause':
                    task_id = input("Task ID: ").strip()
                    if task_id in active_jobs:
                        scheduler.pause_job(task_id)
                        print(f"Pause task '{active_jobs[task_id]}'.")
                    else:
                        print("Cannot find the task having ID {}!".format(task_id))
                
                elif command == 'resume':
                    task_id = input("Enter task ID: ").strip()
                    if task_id in active_jobs:
                        scheduler.resume_job(task_id)
                        print(f"Task '{active_jobs[task_id]}' has been resumed.")
                    else:
                        print("Cannot find task ID!")
                
                elif command == 'list':
                    print("Current task list：")
                    for task_id, task_name in active_jobs.items():
                        job = scheduler.get_job(task_id)
                        status = "pausing" if job.next_run_time is None else "operating"
                        print(f"  - ID: {task_id}, Nmae: {task_name}, Status: {status}")
                
                elif command == 'exit':
                    print("Shut downing Scheduler...")
                    scheduler.shutdown()
                    break
                
                else:
                    print("Invalid command. The command should be one of 'add', 'pause', 'resume', 'list', 'exit', but got {}".format(command))
                
                time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            print("Shut down scheduler.")


def start_task_by_task_id(
    task_id: str = None,
    tasks_config_path: Optional[str] = None,
    send_notification: Optional[bool] = False,
    app_password: Optional[str] = None,
    sender_email: Optional[str] = None,
    recipient_email: Optional[str] = None
): 
    if not tasks_config_path:
        tasks_config_path = Path("config") / "tasks.json"
    config_dir = Path(tasks_config_path).resolve().parents[0]
    tasks_config_df = pd.read_json(tasks_config_path, lines=True, dtype_backend="pyarrow", engine="pyarrow")
    id_filtered_df = tasks_config_df[tasks_config_df["task_id"]==task_id]
    cron_params = id_filtered_df.iloc[0]["cron_params"]
    task_params = id_filtered_df.iloc[0]["task_params"]
    scheduler = BackgroundScheduler()
    scheduler.start()

    if id_filtered_df.iloc[0]["task_type"] == "update_all":
        update_seed = UpgradeScheduler(
            send_notification=send_notification,
            app_password=app_password,
            sender_email=sender_email,
            recipient_email=recipient_email,
            config_dir=config_dir
        )
        scheduler.add_job(
            update_seed.update_task, 
            'cron', 
            id=task_id, 
            kwargs=task_params,
            **cron_params
        )
    elif id_filtered_df.iloc[0]["task_type"] == "by_idx":
        idx_seed = IdxScheduler(
            send_notification=send_notification,
            app_password=app_password,
            sender_email=sender_email,
            recipient_email=recipient_email,
            config_dir=config_dir
        )
        scheduler.add_job(
            idx_seed.start_by_idx_task, 
            'cron', 
            id=task_id, 
            kwargs=task_params,
            **cron_params
        )
    print("Start new task with task_id {}".format(task_id))
        
    try:
        while True:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Shut down the scheduler.")