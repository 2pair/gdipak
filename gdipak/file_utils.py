"""File utility functions for finding, manipulating, and creating files and
directories."""

from pathlib import Path
import re
from typing import List

from gdipak.arg_parser import RecursiveMode

VALID_EXTENSIONS = (".gdi", ".bin", ".raw")
# This regex takes any string of characters that contains "track" followed by a number
# and captures the number.
TRACK_NUMBER_REGEX = re.compile(r"^[\s\S]*track[\s\S]*?([\d]+)", re.IGNORECASE)


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


def get_subdirs_in_dir(directory: str | Path, max_recursion: int = None) -> List[Path]:
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
            subdirs = get_subdirs_in_dir(item, max_recursion)
            dirs.extend(subdirs)

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
        if item.suffix in VALID_EXTENSIONS:
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


def transpose_path(
    game_path: str | Path,
    in_base_path: str | Path,
    out_base_path: str | Path,
    mode: RecursiveMode,
) -> Path:
    """Creates the output path based on the parameters.
    Ex: given game_path = /dir/fighting_games/game_dir; in_base_path = /dir;
     out_base_path = /other_dir;
     if mode = PRESERVE_STRUCTURE out_path = /other_dir/fighting_games/game_dir
     if mode = FLATTEN_STRUCTURE out_path = /other_dir/game_dir

     Args:
        game_path: The path to the game.
        in_base_path: The root directory where the games/game are found.
        out_base_path: The root directory where the games/game are written.
        mode: The to of transpose that will be done.

    Returns:
        The new path. Note that this path is not created on disk by this function.

    Raises:
        ValueError if game_path is not in the directory structure beneath in_base_path.
    """
    game_path = Path(game_path)
    in_base_path = Path(in_base_path)
    local_game_path = game_path.relative_to(in_base_path)
    out_base_path = Path(out_base_path)
    if mode == RecursiveMode.PRESERVE_STRUCTURE:
        return out_base_path / local_game_path
    # else mode == RecursiveMode.FLATTEN_STRUCTURE
    return out_base_path / local_game_path.name


def convert_file_name(file_path: str | Path) -> str:
    """Based on the input file name, generates an output file name.
    Args:
        file_path: A string representing EITHER a path to a file, with extension
            or the file name, with extension.

    Returns:
        A string that GDEMU expects for that file's name.

    Raises:
        ValueError, SyntaxError
    """
    file_path = Path(file_path)
    name = file_path.stem
    ext = file_path.suffix.lower()
    if not ext or ext not in VALID_EXTENSIONS:
        raise ValueError("Invalid file type")
    if ext == ".gdi":
        return "disc.gdi"
    result = TRACK_NUMBER_REGEX.match(name)
    if not result:
        raise SyntaxError("File name does not contain track information")
    track_num = str(int(result.group(1)))  # removes leading zeros
    return "track" + track_num.zfill(2) + ext
