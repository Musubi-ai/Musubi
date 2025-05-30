from typing import Optional
from pathlib import Path
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


def add_task(
    task_type: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config",
    task_name: Optional[str] = None,
    update_pages: Optional[int] = None,
    save_dir: Optional[str] = None,
    start_idx: Optional[int] = 0,
    idx: Optional[int] = 0,
    cron_params: dict = None
):
    """Adds a scheduled task to the scheduler.

    This method creates a task configuration and adds it to the scheduler. It supports two types
    of tasks: 'update_all' and 'by_idx'. The task configuration is written to the task config file
    and then registered with the scheduler server.

    Args:
        task_type: A string indicating the type of task. Must be one of 'update_all' or 'by_idx'.
        host: Optional; the hostname or IP address. Defaults to "127.0.0.1".
        port: Optional; the port number. Defaults to 5000.
        config_dir: Optional; the directory path for configurations. Defaults to "config".
        task_name: Optional; a descriptive name for the task. If None, a default name based on
            task_type will be assigned.
        update_pages: Optional; integer specifying the number of pages to update. If None and
            needed by the task type, defaults to 10.
        save_dir: Optional; string path where task results should be saved.
        start_idx: Optional; integer specifying the starting index for 'update_all' tasks.
            Defaults to 0.
        idx: Optional; integer specifying the specific index for 'by_idx' tasks. Defaults to 0.
        cron_params: Optional; dictionary containing schedule parameters for the task.
        send_notification: Optional; boolean indicating whether to send notifications when the
            task completes. Defaults to False.
        app_password: Optional; string containing the app password for email notifications.
            Required if send_notification is True.
        sender_email: Optional; string containing the sender's email address for notifications.
            Required if send_notification is True.
        recipient_email: Optional; string containing the recipient's email address for notifications.
            Required if send_notification is True.
    """
    controller = Controller(
        host=host,
        port=port,
        config_dir=config_dir
    )
    controller.add_task(
        task_type=task_type,
        task_name=task_name,
        update_pages=update_pages,
        save_dir=save_dir,
        start_idx=start_idx,
        idx=idx,
        cron_params=cron_params
    )


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