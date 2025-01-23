def get_cron_params():
        """
        Retrieve cron arguments from user's input.
        Reference for cron expression:
        https://blog.csdn.net/devil6636252/article/details/109113104
        https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
        """
        print("\nEnter cron arguments（Or just press Enter to input default value '*'）:")
        params = {}
        cron_fields = ['year', 'month', 'week', 'day', 'day_of_week', 'hour', 'minute', 'second']
        
        for field in cron_fields:
            value = input(f"{field}: ").strip()
            params[field] = value if value else '*'

        print("\nThe cron arguments are：")
        for field, value in params.items():
            print(f"{field}: {value}")
            
        confirm = input("\nContinue(y/n): ").lower()
        if confirm != 'y':
            print("Cancel adding new task")
            return None

        return params


def get_idx_task_params():
    print("\nEnter task arguments（the arguments are same as those of start_by_idx function）:")
    params = {}
    cron_fields = ["idx", "upgrade_pages", "save_dir", "task_name"]

    for field in cron_fields:
        value = input(f"{field}: ").strip()
        if (field == "idx") or (field == "upgrade_pages"):
            params[field] = int(value) if value else None
        else:
            params[field] = value if value else None

    print("\nThe start_by_idx arguments are：")
    for field, value in params.items():
        print(f"{field}: {value}")
        
    confirm = input("\nStart the new task(y/n): ").lower()
    if confirm != 'y':
        print("Cancel adding new task")
        return None

    return params


def get_upgrade_task_params():
    print("\nEnter task arguments（the arguments are same as those of start_all function）:")
    params = {}
    cron_fields = ["start_idx", "upgrade_pages", "save_dir", "task_name"]

    for field in cron_fields:
        value = input(f"{field}: ").strip()
        if (field == "idx") or (field == "upgrade_pages"):
            params[field] = int(value) if value else None
        else:
            params[field] = value if value else None

    print("\nThe start_all arguments are：")
    for field, value in params.items():
        print(f"{field}: {value}")
        
    confirm = input("\nStart the new task(y/n): ").lower()
    if confirm != 'y':
        print("Cancel adding new task")
        return None

    return params