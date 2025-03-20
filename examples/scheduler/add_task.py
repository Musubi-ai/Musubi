from musubi.scheduler import Controller


controller = Controller()

def main():
    status_code, _ = controller.check_status()
    if status_code == 200:
        controller.add_task(
        task_type="update_all",
        task_name="test1",
        update_pages=15,
        cron_params={"hour": 12, "second": 5, "minute": 5, "month": 5}
    )


if __name__ == "__main__":
    main()
    # controller.retrieve_task_list()