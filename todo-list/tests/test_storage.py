from pathlib import Path

from todo_list.models import Task
from todo_list.storage import JsonTaskStorage


def test_storage_round_trip(tmp_path: Path) -> None:
    storage = JsonTaskStorage(tmp_path / "nested" / "tasks.json")
    task = Task.create("123", "Write tests")
    task.mark_completed()
    storage.save([task])
    loaded = storage.load()
    assert loaded == [task]
