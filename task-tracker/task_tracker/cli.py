# -*- coding: utf-8 -*-
"""
A simple CLI application used to track and manage your tasks.
    Example:
    python task_tracker add "A new task"
    python task_tracker update 1 "New description"
    python task_tracker mark 1 in-progress
    python task_tracker mark 1 done
    python task_tracker mark 1 todo
    python task_tracker list
    python task_tracker list todo
    python task_tracker list in-progress
    python task_tracker list done
    python task_tracker list not-done
    python task_tracker delete 1
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from task_tracker.task import TaskTracker

task_commands = [
    {
        "cmd": "add",
        "args": [
            {
                "name_or_flags": "description",
                "type": str.strip,
                "help": "A short description of the new task.",
            }
        ],
        "help": "Adding a new task.",
    },
    {
        "cmd": "update",
        "args": [
            {
                "name_or_flags": "id",
                "help": "The ID of the task to be updated.",
            },
            {
                "name_or_flags": "description",
                "type": str.strip,
                "help": "A new short description of the task to be updated.",
            },
        ],
        "help": "Updating the task description by ID.",
    },
    {
        "cmd": "delete",
        "args": [
            {
                "name_or_flags": "id",
                "help": "The ID of the task to be deleted.",
            },
        ],
        "help": "Deleting a task by ID.",
    },
    {
        "cmd": "mark",
        "args": [
            {
                "name_or_flags": "id",
                "help": "The ID of the task to be marked.",
            },
            {
                "name_or_flags": "status",
                "choices": ["todo", "in-progress", "done"],
                "type": str.lower,
                "metavar": "status",
                "help": "The new status of the task to be marked.",
            },
        ],
        "help": "Marking a task as todo, in progress or done.",
    },
    {
        "cmd": "list",
        "args": [
            {
                "name_or_flags": "status",
                "choices": ["todo", "in-progress", "done", "not-done"],
                "type": str.lower,
                "nargs": "?",
                "metavar": "status",
                "help": "The status of the task that to be listed.",
            }
        ],
        "help": "Listing all tasks or listing tasks by status.",
    },
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TaskCli:
    """A simple CLI for task tracker."""

    def __init__(self) -> None:
        self._cache_file: Path = DATA_DIR / "tasks.json"

    def run(self) -> None:
        parser = ArgumentParser(
            prog="task-tracker",
            description="Task tracker is a simple CLI application used to track and manage your tasks.",
        )
        subparsers = parser.add_subparsers(
            title="subcommands",
            description="Add, update, delete, mark and list tasks.",
            metavar="command",
            help="action on tasks",
        )
        for command in task_commands:
            sub_parser = subparsers.add_parser(command["cmd"], help=command["help"])
            for arg in command["args"]:
                sub_parser.add_argument(arg.pop("name_or_flags"), **arg)
                sub_parser.set_defaults(handler=getattr(self, f"handle_{command['cmd']}"))
        args = parser.parse_args()
        if hasattr(args, "handler"):
            args.handler(args)
        else:
            parser.print_help()

    def handle_add(self, args: Namespace) -> None:
        with TaskTracker(self._cache_file) as task_tracker:
            print(f"Task added successfully (ID: {task_tracker.add(args.description)})")

    def handle_update(self, args: Namespace):
        with TaskTracker(self._cache_file) as task_tracker:
            task_tracker.update(args.id, args.description)

    def handle_delete(self, args: Namespace):
        with TaskTracker(self._cache_file) as task_tracker:
            task_tracker.delete(args.id)

    def handle_mark(self, args: Namespace):
        with TaskTracker(self._cache_file) as task_tracker:
            task_tracker.mark_status(args.id, args.status)

    def handle_list(self, args: Namespace):
        task_tracker = TaskTracker(self._cache_file)
        task_tracker.load()
        tasks = task_tracker.list_by_status(args.status)
        if tasks is None:
            return
        if args.status is None:
            print("All tasks\n")
        else:
            print("All tasks that are", *args.status.split("-"), "\n")
        task_format = r"{:5}{:21}{:21}{:13}{}"
        # print head of task list.
        print(task_format.format(*TaskTracker.task_properties))
        print(
            task_format.format(*("-" * n for n in map(len, TaskTracker.task_properties))),
        )
        for task in tasks:
            print(task_format.format(*task))
        print()
