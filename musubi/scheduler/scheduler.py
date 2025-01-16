from apscheduler.schedulers.background import BackgroundScheduler
from ..pipeline import Pipeline
from .notification import Notify
from typing import Optional
import os
import uuid
import time
from datetime import datetime


def get_cron_params():
        """Retrieve cron arguments from user's input"""
        print("\nEnter cron arguments（Press Enter to enter default value '*'）：")
        params = {}
        cron_fields = ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second']
        
        for field in cron_fields:
            value = input(f"{field}: ").strip()
            params[field] = value if value else '*'

        print("\nThe cron arguments are：")
        for field, value in params.items():
            print(f"{field}: {value}")
            
        confirm = input("\nStart the new task(y/n): ").lower()
        if confirm != 'y':
            print("Cancel adding new task")
            return None

        return params


class CrawlScheduler:
    """
    Periodically crawl certain website based on idx.
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
                raise ValueError("To let scheduler send notification, please set app_password.")
            self.notify = Notify(
                app_password=self.app_password,
                sender_email=sender_email,
                recipient_email=recipient_email
            )

    def task(
        self,
        website_path="config/websites.json",
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        idx: Optional[int] = None,
        upgrade_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: str = None,
        task_name: str = None
    ):
        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Start scheduled crawling",
                body="Start scheduled task {} at {}".format(task_name, datetime.now())
            )

        pipe = Pipeline(website_path=website_path)
        pipe.start_by_idx(
            start_page=start_page,
            start_idx=start_idx,
            idx=idx,
            upgrade_pages=upgrade_pages,
            sleep_time=sleep_time,
            save_dir=save_dir
        )

        if self.notify:
            self.notify.send_gmail(
                subject="Musubi: Finished scheduled crawling",
                body="Finished scheduled task {} at {}".format(task_name, datetime.now())
            )
    
    def launch_scheduler(
        self,
        start_page: Optional[int] = 0,
        start_idx: Optional[int] = 0,
        idx: Optional[int] = None,
        upgrade_pages: Optional[int] = None,
        sleep_time: Optional[int] = None,
        save_dir: str = None
    ):
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
                        # Generate unique task id by uuid4
                        job_id = uuid.uuid4()
                        
                        # Add task
                        scheduler.add_job(
                            self.task, 
                            'cron', 
                            id=job_id, 
                            kwargs={
                                "start_page": start_page, 
                                "start_idx": start_idx, 
                                "idx": idx, 
                                "upgrade_pages": upgrade_pages, 
                                "sleep_time": sleep_time,
                                "save_dir": save_dir
                            },
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





