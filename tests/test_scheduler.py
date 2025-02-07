from ..musubi.scheduler import IdxScheduler


def test_IdxScheduler():
    idx_scheduler = IdxScheduler()
    idx_scheduler.launch_scheduler()