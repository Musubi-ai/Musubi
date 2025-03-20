from musubi.scheduler import Controller
from typing import Optional


def launch_scheduler(config_dir: Optional[str] = None):
    controller = Controller(config_dir=config_dir)
    controller.launch_scheduler()


if __name__ == "__main__":
    launch_scheduler()