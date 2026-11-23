"""Sort the files in a directory into category folders.

Files are grouped by extension into Images, Documents, Audio, Video,
Archives, Code, and Other. Subdirectories are left alone, existing files
are never overwritten (a numeric suffix is added instead), and a dry run
mode reports the planned moves without touching anything.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
               ".tif", ".tiff", ".ico", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".odt", ".rtf",
                  ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".epub"},
    "Audio": {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"},
    "Video": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".c", ".cpp", ".java"},
}

DEFAULT_CATEGORY = "Other"


def get_category(path: Path) -> str:
    """Return the category name for *path* based on its extension."""
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return DEFAULT_CATEGORY


def unique_destination(destination: Path, taken: set[Path] | None = None) -> Path:
    """Return *destination*, or a ``name_1`` style variant if it exists.

    Destinations already reserved in *taken* (planned moves that have
    not happened yet) count as taken too, so two same named files from
    different folders never plan onto the same path.
    """
    taken = taken if taken is not None else set()
    if destination not in taken and not destination.exists():
        return destination
    stem, suffix = destination.stem, destination.suffix
    counter = 1
    while True:
        candidate = destination.with_name(f"{stem}_{counter}{suffix}")
        if candidate not in taken and not candidate.exists():
            return candidate
        counter += 1


def _already_organized(directory: Path, path: Path) -> bool:
    """Return True if *path* already sits in a top level category folder."""
    return (
        path.parent.parent == directory
        and path.parent.name in set(CATEGORIES) | {DEFAULT_CATEGORY}
    )


def plan_moves(directory: Path, recursive: bool = False) -> list[tuple[Path, Path]]:
    """Return the (source, destination) moves organizing *directory* would make.

    With ``recursive=True`` files in subfolders are moved up into the top
    level category folders too, except files that are already organized.
    """
    directory = Path(directory)
    if recursive:
        entries = sorted(entry for entry in directory.rglob("*") if entry.is_file())
    else:
        entries = sorted(directory.iterdir())
    moves = []
    planned: set[Path] = set()
    for entry in entries:
        if not entry.is_file():
            continue
        if recursive and _already_organized(directory, entry):
            continue
        target_dir = directory / get_category(entry)
        destination = unique_destination(target_dir / entry.name, planned)
        if destination == entry:
            continue
        planned.add(destination)
        moves.append((entry, destination))
    return moves


def organize_directory(
    directory: Path, dry_run: bool = False, recursive: bool = False
) -> list[tuple[Path, Path]]:
    """Move files in *directory* into category folders and return the moves.

    With ``dry_run=True`` nothing is created or moved; the planned moves
    are returned instead. With ``recursive=True`` files in subfolders
    are organized too.

    Raises:
        NotADirectoryError: if *directory* does not exist or is not a folder.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")
    moves = plan_moves(directory, recursive=recursive)
    if dry_run:
        return moves
    for source, destination in moves:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
    return moves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sort a directory into category folders.")
    parser.add_argument("directory", help="folder to organize")
    parser.add_argument(
        "--dry-run", action="store_true", help="print planned moves, change nothing"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="organize files in subfolders too",
    )
    args = parser.parse_args(argv)

    try:
        moves = organize_directory(
            Path(args.directory), dry_run=args.dry_run, recursive=args.recursive
        )
    except NotADirectoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for source, destination in moves:
        prefix = "would move" if args.dry_run else "moved"
        print(f"{prefix}: {source.name} -> {destination.parent.name}/{destination.name}")
    print(f"{len(moves)} file(s) {'planned' if args.dry_run else 'organized'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
