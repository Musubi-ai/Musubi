from typing import Optional
from pathlib import Path
from ...scheduler import Controller, Scheduler


def launch_scheduler(
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    log_path: Optional[str] = None
):
    """Launches the scheduler with the current configuration.

        Args:
            config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
            website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
            host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
            port (Optional[int]): The port number. Defaults to 5000.
            log_path (Optional[str], default to None): If have, save the log into specified json file.
    """
    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    scheduler = Scheduler(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port,
        log_path=log_path
    )
    scheduler.run()


def shutdown_scheduler(
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Shuts down the scheduler with the current configuration.

    Creates a Controller instance and calls its shutdown_scheduler method
    to gracefully terminate the scheduler service.

    Args:
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.

    Returns:
        The response from the shutdown request, typically a status message
        indicating success or failure.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    res = controller.shutdown_scheduler()
    return res


def check_status(
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Checks the status of the controller server.

    Args:
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    
    Returns:
        str: A message containing the status code and response text if the 
            request was successful, or an error message if the request failed.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    res = controller.check_status()
    return res


def retrieve_task_list(
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Retrieves the list of tasks from the scheduler server.

    Args:
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    
    Returns:
        requests.Response: The response object from the API call if successful.
        str: An error message if the request fails.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    res = controller.retrieve_task_list()
    return res


def add_task(
    task_type: str,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000,
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
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
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
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
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
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
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Starts a task with the specified task_id from existing configuration.
    
    Args:
        task_id: The unique identifier of the task to pause.
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    controller.start_task_from_config(task_id=task_id)


def pause_task(
    task_id: str,
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Pauses a task with the specified task_id.
    
    Args:
        task_id: The unique identifier of the task to pause.
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    controller.pause_task(task_id=task_id)


def resume_task(
    task_id: str,
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Resumes a previously paused task with the specified task_id.
    
    Args:
        task_id: The unique identifier of the task to resume.
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    controller.resume_task(task_id=task_id)

def remove_task(
    task_id: str,
    config_dir: Optional[str] = "config",
    website_config_path: Optional[str] = None,
    host: Optional[str] = "127.0.0.1",
    port: Optional[int] = 5000
):
    """Removes a task with the specified task_id from the scheduler.
    
    Args:
        task_id: The unique identifier of the task to remove.
        config_dir (Optional[str]): The directory path for configurations. Defaults to "config".
        website_config_path (Optional[str]): The json path for website configurations. Defaults to None.
        host (Optional[str]): The hostname or IP address. Defaults to "127.0.0.1".
        port (Optional[int]): The port number. Defaults to 5000.
    """
    controller = Controller(
        config_dir=config_dir,
        website_config_path=website_config_path,
        host=host,
        port=port
    )
    controller.remove_task(task_id=task_id)