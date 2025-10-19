from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SchedulerInfo:
    """Container for scheduler configuration and runtime state.

    This dataclass stores general configuration paths and active task
    information used by the scheduler server.
    """
    config_dir: str = field(default="config")
    website_config_path: str = field(default=None)
    active_tasks: dict = field(default_factory=dict)


@dataclass
class GeneralRequest:
    """General-purpose request structure for scheduler API endpoints.
    """
    task_id: str = field(default=None)


@dataclass
class GeneralResponse:
    """Standard response object for API endpoints returning a message.
    """
    message: str = field(default="")


@dataclass
class TasksResponse:
    """Response object containing task-related information.
    """
    message: str = field(default="")
    tasks: List[Dict] = field(default_factory=list)


@dataclass
class StartTaskResponse:
    """Response object for a task start request.
    """
    message: str = field(default="")
    task_data: dict = field(default_factory=dict)



