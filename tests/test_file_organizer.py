from pathlib import Path

import pytest

from file_organizer import get_category, organize_directory, unique_destination


def make_files(root: Path, names: list[str]) -> None:
    for name in names:
        (root / name).write_text("x", encoding="utf-8")


def test_get_category_by_extension():
    assert get_category(Path("photo.JPG")) == "Images"
    assert get_category(Path("notes.pdf")) == "Documents"
    assert get_category(Path("song.mp3")) == "Audio"
    assert get_category(Path("clip.mkv")) == "Video"
    assert get_category(Path("backup.zip")) == "Archives"
    assert get_category(Path("app.py")) == "Code"
    assert get_category(Path("mystery.xyz")) == "Other"
    assert get_category(Path("no_extension")) == "Other"
    assert get_category(Path("sheet.xlsx")) == "Documents"
    assert get_category(Path("data.csv")) == "Documents"
    assert get_category(Path("book.epub")) == "Documents"
    assert get_category(Path("scan.tiff")) == "Images"
    assert get_category(Path("icon.ico")) == "Images"
    assert get_category(Path("voice.aac")) == "Audio"
    assert get_category(Path("movie.flv")) == "Video"


def test_organize_moves_files_into_categories(tmp_path):
    make_files(tmp_path, ["a.png", "b.txt", "c.mp3", "d.bin"])
    moves = organize_directory(tmp_path)
    assert len(moves) == 4
    assert (tmp_path / "Images" / "a.png").is_file()
    assert (tmp_path / "Documents" / "b.txt").is_file()
    assert (tmp_path / "Audio" / "c.mp3").is_file()
    assert (tmp_path / "Other" / "d.bin").is_file()


def test_dry_run_changes_nothing(tmp_path):
    make_files(tmp_path, ["a.png"])
    moves = organize_directory(tmp_path, dry_run=True)
    assert len(moves) == 1
    assert (tmp_path / "a.png").is_file()
    assert not (tmp_path / "Images").exists()


def test_subdirectories_are_left_alone(tmp_path):
    (tmp_path / "keep").mkdir()
    (tmp_path / "keep" / "inner.txt").write_text("x", encoding="utf-8")
    make_files(tmp_path, ["top.txt"])
    organize_directory(tmp_path)
    assert (tmp_path / "keep" / "inner.txt").is_file()
    assert (tmp_path / "Documents" / "top.txt").is_file()


def test_existing_files_are_never_overwritten(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.png").write_text("original", encoding="utf-8")
    make_files(tmp_path, ["a.png"])
    organize_directory(tmp_path)
    assert (tmp_path / "Images" / "a.png").read_text(encoding="utf-8") == "original"
    assert (tmp_path / "Images" / "a_1.png").is_file()


def test_unique_destination_suffixes():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "f.txt"
        assert unique_destination(target) == target
        target.write_text("x", encoding="utf-8")
        assert unique_destination(target) == Path(tmp) / "f_1.txt"


def test_missing_directory_rejected(tmp_path):
    with pytest.raises(NotADirectoryError):
        organize_directory(tmp_path / "does-not-exist")


def test_recursive_organizes_nested_files(tmp_path):
    (tmp_path / "nested" / "deep").mkdir(parents=True)
    (tmp_path / "nested" / "photo.png").write_text("x", encoding="utf-8")
    (tmp_path / "nested" / "deep" / "notes.txt").write_text("x", encoding="utf-8")
    make_files(tmp_path, ["top.mp3"])
    moves = organize_directory(tmp_path, recursive=True)
    assert len(moves) == 3
    assert (tmp_path / "Images" / "photo.png").is_file()
    assert (tmp_path / "Documents" / "notes.txt").is_file()
    assert (tmp_path / "Audio" / "top.mp3").is_file()


def test_recursive_leaves_already_organized_files(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "done.png").write_text("x", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "new.png").write_text("x", encoding="utf-8")
    moves = organize_directory(tmp_path, recursive=True)
    assert len(moves) == 1
    assert (tmp_path / "Images" / "done.png").is_file()
    assert (tmp_path / "Images" / "new.png").is_file()


def test_recursive_keeps_same_named_files_from_different_folders(tmp_path):
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    (tmp_path / "one" / "notes.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two" / "notes.txt").write_text("two", encoding="utf-8")
    organize_directory(tmp_path, recursive=True)
    assert (tmp_path / "Documents" / "notes.txt").is_file()
    assert (tmp_path / "Documents" / "notes_1.txt").is_file()
    contents = {
        (tmp_path / "Documents" / "notes.txt").read_text(encoding="utf-8"),
        (tmp_path / "Documents" / "notes_1.txt").read_text(encoding="utf-8"),
    }
    assert contents == {"one", "two"}


def test_recursive_dry_run_changes_nothing(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "photo.png").write_text("x", encoding="utf-8")
    moves = organize_directory(tmp_path, dry_run=True, recursive=True)
    assert len(moves) == 1
    assert (tmp_path / "nested" / "photo.png").is_file()
    assert not (tmp_path / "Images").exists()
