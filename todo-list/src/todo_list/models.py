from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class Task:
    id: str
    title: str
    completed: bool = False
    created_at: str = ""
    completed_at: str | None = None

    @classmethod
    def create(cls, task_id: str, title: str) -> "Task":
        return cls(
            id=task_id,
            title=title,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def mark_completed(self) -> None:
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Task":
        required = ("id", "title", "completed", "created_at")
        if any(key not in data for key in required):
            raise ValueError("Task data is missing required fields")

        task_id = data["id"]
        title = data["title"]
        completed = data["completed"]
        created_at = data["created_at"]
        completed_at = data.get("completed_at")

        if not all(isinstance(value, str) for value in (task_id, title, created_at)):
            raise ValueError("Task id, title, and created_at must be strings")
        if not isinstance(completed, bool):
            raise ValueError("Task completed must be a boolean")
        if completed_at is not None and not isinstance(completed_at, str):
            raise ValueError("Task completed_at must be a string or null")

        return cls(
            id=task_id,
            title=title,
            completed=completed,
            created_at=created_at,
            completed_at=completed_at,
        )
