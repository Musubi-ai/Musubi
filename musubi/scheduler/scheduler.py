from apscheduler.schedulers.background import BackgroundScheduler
from ..pipeline import Pipeline
from .notification import Notify
from .params_retriever import get_cron_params, get_idx_task_params, get_upgrade_task_params
from typing import Optional
import os
import uuid
import time
from datetime import datetime
from abc import ABC, abstractmethod


class BaseScheduler(ABC):
    def __init__(
        self,
        send_notification: Optional[bool] = False,
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
                raise ValueError("To let scheduler send notification, please set app_password.")
            self.notify = Notify(
                app_password=self.app_password,
                sender_email=sender_email,
                recipient_email=recipient_email
            )

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
    ):
        super().__init__(send_notification, app_password, sender_email, recipient_email)

    def start_by_idx_task(
        self,
        website_path="config/websites.json",
        idx: int = None,
        upgrade_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
        task_name: str = None
    ):
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled crawling",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )

        pipe = Pipeline(website_path=website_path)
        pipe.start_by_idx(
            idx=idx,
            upgrade_pages=upgrade_pages,
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
                        # Generate unique task id by uuid4
                        job_id = uuid.uuid4()
                        
                        # Add task
                        scheduler.add_job(
                            self.start_by_idx_task, 
                            'cron', 
                            id=job_id, 
                            kwargs=task_params,
                            **cron_params
                        )
                        active_jobs[job_id] = task_name
                        print(f"Add task '{task_name}', ID: {job_id}")

                    except ValueError as e:
                        print(f"ValueError: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        continue
                
                elif command == 'pause':
                    job_id = input("Task ID: ").strip()
                    if job_id in active_jobs:
                        scheduler.pause_job(job_id)
                        print(f"Pause task '{active_jobs[job_id]}'.")
                    else:
                        print("Cannot find the task having ID {}!".format(job_id))
                
                elif command == 'resume':
                    job_id = input("Enter task ID: ").strip()
                    if job_id in active_jobs:
                        scheduler.resume_job(job_id)
                        print(f"Task '{active_jobs[job_id]}' has been resumed.")
                    else:
                        print("Cannot find task ID!")
                
                elif command == 'list':
                    print("Current task list：")
                    for job_id, task_name in active_jobs.items():
                        job = scheduler.get_job(job_id)
                        status = "pausing" if job.next_run_time is None else "operating"
                        print(f"  - ID: {job_id}, Nmae: {task_name}, Status: {status}")
                
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
    ):
        super().__init__(send_notification, app_password, sender_email, recipient_email)

    def start_all_task(
        self,
        website_path="config/websites.json",
        start_idx: Optional[int] = 0,
        upgrade_pages: Optional[int] = None,
        save_dir: Optional[str] = None,
        task_name: str = None
    ):
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled upgrading",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )

        pipe = Pipeline(website_path=website_path)
        pipe.start_all(
            start_idx=start_idx,
            upgrade_pages=upgrade_pages,
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
                        task_params = get_upgrade_task_params()
                        # Generate unique task id by uuid4
                        job_id = uuid.uuid4()
                        
                        # Add task
                        scheduler.add_job(
                            self.start_all_task, 
                            'cron', 
                            id=job_id, 
                            kwargs=task_params,
                            **cron_params
                        )
                        active_jobs[job_id] = task_name
                        print(f"Add task '{task_name}', ID: {job_id}")

                    except ValueError as e:
                        print(f"ValueError: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        continue
                
                elif command == 'pause':
                    job_id = input("Task ID: ").strip()
                    if job_id in active_jobs:
                        scheduler.pause_job(job_id)
                        print(f"Pause task '{active_jobs[job_id]}'.")
                    else:
                        print("Cannot find the task having ID {}!".format(job_id))
                
                elif command == 'resume':
                    job_id = input("Enter task ID: ").strip()
                    if job_id in active_jobs:
                        scheduler.resume_job(job_id)
                        print(f"Task '{active_jobs[job_id]}' has been resumed.")
                    else:
                        print("Cannot find task ID!")
                
                elif command == 'list':
                    print("Current task list：")
                    for job_id, task_name in active_jobs.items():
                        job = scheduler.get_job(job_id)
                        status = "pausing" if job.next_run_time is None else "operating"
                        print(f"  - ID: {job_id}, Nmae: {task_name}, Status: {status}")
                
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