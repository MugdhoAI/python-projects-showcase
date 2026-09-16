from pathlib import Path

import pytest

from todo_list.service import TaskNotFoundError, TaskService
from todo_list.storage import JsonTaskStorage, StorageError


def make_service(tmp_path: Path) -> TaskService:
    return TaskService(JsonTaskStorage(tmp_path / "tasks.json"))


def test_add_task_persists_and_normalizes_title(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    task = service.add_task("  Buy groceries  ")
    assert task.title == "Buy groceries"
    assert service.list_tasks() == [task]


def test_empty_title_is_rejected(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(ValueError, match="cannot be empty"):
        service.add_task("   ")


def test_title_over_200_characters_is_rejected(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(ValueError, match="200 characters"):
        service.add_task("x" * 201)


def test_complete_task_changes_status(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    task = service.add_task("Ship project")
    completed = service.complete_task(task.id)
    assert completed.completed is True
    assert completed.completed_at is not None
    assert service.list_tasks("pending") == []
    assert service.list_tasks("completed") == [completed]


def test_completing_missing_task_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(TaskNotFoundError, match="Task not found"):
        service.complete_task("missing-id")


def test_delete_task_removes_it(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    task = service.add_task("Remove me")
    deleted = service.delete_task(task.id)
    assert deleted == task
    assert service.list_tasks() == []


def test_delete_missing_task_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(TaskNotFoundError):
        service.delete_task("missing-id")


def test_invalid_status_is_rejected(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(ValueError, match="Status must be one of"):
        service.list_tasks("invalid")


def test_corrupt_storage_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text("not json", encoding="utf-8")
    service = TaskService(JsonTaskStorage(path))
    with pytest.raises(StorageError, match="Could not read task file"):
        service.list_tasks()
