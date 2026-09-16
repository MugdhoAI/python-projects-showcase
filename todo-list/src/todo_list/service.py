from __future__ import annotations

from uuid import uuid4

from .models import Task
from .storage import JsonTaskStorage


class TaskNotFoundError(LookupError):
    """Raised when a requested task does not exist."""


class TaskService:
    def __init__(self, storage: JsonTaskStorage) -> None:
        self.storage = storage

    def list_tasks(self, status: str = "all") -> list[Task]:
        tasks = self.storage.load()
        if status == "pending":
            return [task for task in tasks if not task.completed]
        if status == "completed":
            return [task for task in tasks if task.completed]
        if status == "all":
            return tasks
        raise ValueError("Status must be one of: all, pending, completed")

    def add_task(self, title: str) -> Task:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Task title cannot be empty")
        if len(normalized_title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

        tasks = self.storage.load()
        task = Task.create(str(uuid4()), normalized_title)
        tasks.append(task)
        self.storage.save(tasks)
        return task

    def complete_task(self, task_id: str) -> Task:
        tasks = self.storage.load()
        task = self._find(tasks, task_id)
        task.mark_completed()
        self.storage.save(tasks)
        return task

    def delete_task(self, task_id: str) -> Task:
        tasks = self.storage.load()
        task = self._find(tasks, task_id)
        tasks.remove(task)
        self.storage.save(tasks)
        return task

    @staticmethod
    def _find(tasks: list[Task], task_id: str) -> Task:
        normalized_id = task_id.strip()
        if not normalized_id:
            raise TaskNotFoundError("Task ID cannot be empty")
        for task in tasks:
            if task.id == normalized_id:
                return task
        raise TaskNotFoundError(f"Task not found: {normalized_id}")
