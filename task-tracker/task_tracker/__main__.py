import sys

# If the module is run as a script or the __main__ file of the module is directly executed,
# import task_tracker module manually.
if not __spec__ or not __spec__.parent:
    from pathlib import Path

    path = Path(__file__).resolve().parent
    if sys.path[0] == str(path):
        sys.path[0] = str(path.parent)
    else:
        sys.path.insert(0, str(path.parent))
    from task_tracker.cli import TaskCli

    sys.path.pop(0)
else:
    from task_tracker.cli import TaskCli

TaskCli().run()
