from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SchedulerInfo:
    config_dir: str = field(default="config")
    website_config_path: str = field(default=None)
    active_tasks: dict = field(default_factory=dict)


@dataclass
class GeneralRequest:
    task_id: str = field(default=None)


@dataclass
class GeneralResponse:
    message: str = field(default="")


@dataclass
class TasksResponse:
    message: str = field(default="")
    tasks: List[Dict] = field(default_factory=list)


@dataclass
class StartTaskResponse:
    message: str = field(default="")
    task_data: dict = field(default_factory=dict)



