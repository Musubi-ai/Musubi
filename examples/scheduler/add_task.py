from musubi.scheduler import Controller
from typing import Optional


controller = Controller()

def main():
    # First check the status of scheduler server
    status_code, msg = controller.check_status()
    if status_code == "200":
        ...


if __name__ == "__main__":
    status_code, msg = main()
    print(status_code)