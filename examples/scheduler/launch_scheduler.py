from musubi.scheduler import Controller
from typing import Optional


def launch_scheduler(
    config_dir: Optional[str] = None,
    log_path: Optional[str] = None
):
    controller = Controller(config_dir=config_dir, log_path=log_path)
    controller.launch_scheduler()


if __name__ == "__main__":
    launch_scheduler(log_path="logs/scheduler.log")