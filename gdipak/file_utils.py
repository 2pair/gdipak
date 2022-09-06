"""File utility functions."""

from pathlib import Path
from typing import List

from gdipak.file_processor import FileProcessor


def write_file(in_file: str | Path, out_file: str | Path) -> None:
    """Generates a file with the given contents.

    Args:
        in_file: a path to a file from which to copy data.
        out_file: a path to which to write the data.
    """
    if in_file == out_file:
        return
    out_file = Path(out_file)
    out_dir = out_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    in_file = Path(in_file)
    out_file.write_bytes(in_file.read_bytes())


def get_sub_dirs_in_dir(directory: str | Path, max_recursion: int = None) -> List[Path]:
    """Searches in a given directory for subdirectories.

    Args:
        directory: A path to a directory to search in.
        max_recursion: The number of times to look in sub-directories for more
          directories.

    Returns:
        A  list of subdirectories.
    """
    dirs = []
    for item in Path(directory).iterdir():
        if not item.is_dir():
            continue
        dirs.append(item)
        if max_recursion != 0:
            if max_recursion is not None:
                max_recursion -= 1
            sub_dirs = get_sub_dirs_in_dir(item, max_recursion)
            dirs.extend(sub_dirs)

    return dirs


def get_game_files_in_dir(directory: str | Path) -> List[Path]:
    """Searches in a given directory for files relevant to the GDI game format.

    Args:
        directory: A path to a directory to search in.

    Returns:
        A  list of file paths.
    """
    files = []
    for item in Path(directory).iterdir():
        if not item.is_file():
            continue
        if item.suffix in FileProcessor.valid_extensions:
            files.append(item)
    return files


def write_name_file(out_dir: str | Path, gdi_file: str | Path) -> None:
    """Creates an empty text file with the name of the given gdi file.

    Args:
        out_dir: The location to write the name file.
        gdi_file: The file who's name will be used for the name file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_file_name = Path(gdi_file).stem
    out_file = out_dir / txt_file_name
    out_file.touch()
