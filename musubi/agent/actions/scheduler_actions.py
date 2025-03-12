from typing import Optional
from pathlib import Path
from rich.console import Console
from ...scheduler import Controller, Scheduler


def launch_scheduler(
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Launches the scheduler with the current configuration.

        Args:
            host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
            port (Optional[int]): The port number. Defaults to 5000.
            config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
    """
    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    scheduler = Scheduler(
        config_dir=config_dir,
        host=host,
        port=port
    )
    scheduler.run()


def shutdown_scheduler(
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Shuts down the scheduler with the current configuration.

    Creates a Controller instance and calls its shutdown_scheduler method
    to gracefully terminate the scheduler service.

    Args:
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".

    Returns:
        The response from the shutdown request, typically a status message
        indicating success or failure.
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    res = controller.shutdown_scheduler()
    return res


def check_status(
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Checks the status of the controller server.

    Args:
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    
    Returns:
        str: A message containing the status code and response text if the 
            request was successful, or an error message if the request failed.
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    res = controller.check_status()
    return res


def retrieve_task_list(
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Retrieves the list of tasks from the scheduler server.

    Args:
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    
    Returns:
        requests.Response: The response object from the API call if successful.
        str: An error message if the request fails.
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    res = controller.retrieve_task_list()
    return res


def add_task():
    ...


def start_task_from_config(
    task_id: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Starts a task with the specified task_id from existing configuration.
    
    Args:
        task_id: The unique identifier of the task to pause.
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    controller.start_task_from_config(task_id=task_id)

def pause_task(
    task_id: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Pauses a task with the specified task_id.
    
    Args:
        task_id: The unique identifier of the task to pause.
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    controller.pause_task(task_id=task_id)


def resume_task(
    task_id: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Resumes a previously paused task with the specified task_id.
    
    Args:
        task_id: The unique identifier of the task to resume.
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    controller.resume_task(task_id=task_id)

def remove_task(
    task_id: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config"
):
    """Removes a task with the specified task_id from the scheduler.
    
    Args:
        task_id: The unique identifier of the task to remove.
        host: The hostname or IP address. Defaults to "127.0.0.1".
        port: The port number. Defaults to 5000.
        config_dir: The directory path for configurations. Defaults to "config".
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    controller.remove_task(task_id=task_id)