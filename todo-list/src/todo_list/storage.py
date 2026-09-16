from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import Task


class StorageError(RuntimeError):
    """Raised when task data cannot be read or written safely."""


class JsonTaskStorage:
    def __init__(self, path: Path) -> None:
        self.path = path.expanduser()

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Could not read task file: {self.path}") from exc

        if not isinstance(raw, list):
            raise StorageError("Task file must contain a JSON array")

        try:
            return [Task.from_dict(item) for item in raw if isinstance(item, dict)]
        except ValueError as exc:
            raise StorageError("Task file contains invalid task data") from exc

    def save(self, tasks: list[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            [task.to_dict() for task in tasks],
            indent=2,
            ensure_ascii=False,
        )

        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(payload)
                temporary.write("\n")
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, self.path)
        except OSError as exc:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)
            raise StorageError(f"Could not write task file: {self.path}") from exc
