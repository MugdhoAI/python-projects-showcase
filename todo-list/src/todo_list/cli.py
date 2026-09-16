from __future__ import annotations

import argparse
import os
from pathlib import Path

from .service import TaskNotFoundError, TaskService
from .storage import JsonTaskStorage, StorageError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Manage a persistent command-line to-do list.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--status",
        choices=("all", "pending", "completed"),
        default="all",
        help="Filter tasks by status (default: all)",
    )

    complete_parser = subparsers.add_parser("done", help="Mark a task as completed")
    complete_parser.add_argument("task_id", help="Task ID")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")

    return parser


def data_path() -> Path:
    configured = os.getenv("TODO_LIST_DATA_FILE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".todo-list" / "tasks.json"


def format_task(task) -> str:
    marker = "x" if task.completed else " "
    return f"[{marker}] {task.id}  {task.title}"


def run(args: argparse.Namespace, service: TaskService) -> int:
    if args.command == "add":
        task = service.add_task(args.title)
        print(f"Added: {task.title}")
        print(f"ID: {task.id}")
        return 0

    if args.command == "list":
        tasks = service.list_tasks(args.status)
        if not tasks:
            print("No tasks found.")
            return 0
        for task in tasks:
            print(format_task(task))
        return 0

    if args.command == "done":
        task = service.complete_task(args.task_id)
        print(f"Completed: {task.title}")
        return 0

    if args.command == "delete":
        task = service.delete_task(args.task_id)
        print(f"Deleted: {task.title}")
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    service = TaskService(JsonTaskStorage(data_path()))

    try:
        return run(args, service)
    except (TaskNotFoundError, StorageError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
