# -*- coding: utf-8 -*-
"""
A simple CLI application used to track and manage your tasks.
    Example:
    python task_tracker
    task-tracker> add "A new task"
    task-tracker> update 1 "New description"
    task-tracker> mark 1 in-progress
    task-tracker> mark 1 done
    task-tracker> mark 1 todo
    task-tracker> list
    task-tracker> list todo
    task-tracker> list in-progress
    task-tracker> list done
    task-tracker> list not-done
    task-tracker> delete 1
"""

from cmd import Cmd
from pathlib import Path

from task_tracker.task import TaskTracker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TaskCli(Cmd):
    """A simple CLI for task tracker."""

    intro = 'Task tracker is a simple CLI application used to track and manage your tasks.\nType "help" for more information.'
    prompt = "task-tracker> "

    def __init__(self) -> None:
        super().__init__()
        self._task_tracker = TaskTracker(DATA_DIR / "tasks.json")

    @staticmethod
    def remove_quote(s: str) -> str:
        """
        If the string is enclosed with a pair of quotes (" or '),
        delete the quotes first, and then remove the leading and trailing whitespaces.
        For example, if s is "'       hello  world   '", than return "helo world".
        """
        if len(s) >= 2 and s[0] in ('"', "'") and s[0] == s[-1]:
            return s[1:-1].strip()
        return s

    def do_add(self, line: str) -> None:
        """
        Usage: add <description>

        Add a new task.
        """
        if not line:
            print("task-tracker: 'description' is required.")
            return
        if line in ("-h", "--help"):
            self.do_help("add")
            return
        if id := self._task_tracker.add(self.remove_quote(line)):
            print(f"Task added successfully (ID: {id})")

    def do_update(self, line: str) -> None:
        """
        Usage: update <id> <description>

        Update the task description by ID.
        """
        if not line:
            print("task-tracker: 'id' and 'description' are required.")
            return
        if line in ("-h", "--help"):
            self.do_help("update")
            return
        id, *description = line.split(maxsplit=1)
        if not description:
            print("task-tracker: 'description' is required.")
            return
        self._task_tracker.update(id, self.remove_quote(description[0]))

    def do_delete(self, line: str) -> None:
        """
        Usage: delete <id>

        Delete a task by ID.
        """
        if not line:
            print("task-tracker: 'id' is required.")
            return
        if line in ("-h", "--help"):
            self.do_help("delete")
            return
        self._task_tracker.delete(line)

    def do_mark(self, line: str) -> None:
        """
        Usage: mark <id> {"todo" | "in-progress" | "done"}

        Mark a task as todo, in progress or done by ID.
        """
        if not line:
            print("task-tracker: 'id' and 'status' are required.")
            return
        if line in ("-h", "--help"):
            self.do_help("mark")
            return
        id, *status = line.split(maxsplit=1)
        if not status:
            print("task-tracker: 'status' is required.")
            return
        self._task_tracker.mark_status(id, str.lower(status[0]))

    def do_list(self, line: str) -> None:
        """
        Usage: list [{"todo" | "in-progress" | "done" | "not-done"}]

        List all tasks or list tasks by status.
        """
        if line in ("-h", "--help"):
            self.do_help("list")
            return
        tasks = self._task_tracker.list_by_status(str.lower(line))
        if tasks is None:
            return
        if line == "":
            print("All tasks")
        else:
            print("All tasks that are", *line.split("-"))

        task_format = r"{:5}{:21}{:21}{:13}{}"
        # print head of task list.
        print(task_format.format(*TaskTracker.task_properties))
        print(
            task_format.format(*("-" * n for n in map(len, TaskTracker.task_properties))),
        )
        for task in tasks:
            print(task_format.format(*task))
        print()

    def do_exit(self, line: str) -> bool:
        """
        Usage: exit

        Exit task tracker cli.
        """
        return True

    def do_EOF(self, line: str) -> bool:
        """Exit task tracker cli by pressing Ctrl-D (Unix or Linux) or Ctrl-Z (Windows)."""
        return True

    def preloop(self) -> None:
        """Load tasks when the cmdloop() method is called."""
        self._task_tracker.load()

    def postloop(self) -> None:
        """Save tasks when the cmdloop() method is about to return."""
        self._task_tracker.save()

    def default(self, line: str) -> None:
        cmd, *_ = line.partition(" ")
        print(f"task-tracker: '{cmd}' is not a task-tracker command. See 'help'.")

    def emptyline(self) -> bool:
        "Do nothing when an empty line is entered."
        return False
