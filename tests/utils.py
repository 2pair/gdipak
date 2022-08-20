"""Functions used across various unit tests."""

from os import path, scandir
import random
import re
from typing import List, Tuple


def make_files(tmpdir: str, game_name: str) -> Tuple[str, List[str], List[str]]:
    """Creates a typical game directory.

    Args:
        tmpdir: A directory where the game files' directory will be made.
        game_name: What's this bad boy gonna be called?

    Returns:
        3-tuple:
        - The path to the game's directory
        - A list of file names that were created
        - A list of file extensions that were created (used in some tests)
    """
    file_names = (
        game_name + ".gdi",
        game_name + "(track1).bin",
        game_name + "(track2).bin",
        game_name + "(track3).raw",
    )
    game_dir = tmpdir.mkdir(game_name)
    file_extensions = []
    for file_name in file_names:
        file_path = game_dir.join(file_name)
        file_path.write("")
        _1, ext = path.splitext(file_name)
        if ext not in file_extensions:
            file_extensions.append(ext)

    return game_dir, file_names, file_extensions


# pylint: disable=too-many-locals
def make_gdi_contents(game_name: str) -> str:
    """Creates the contents of a GDI file as it is before being converted.

    Args:
      game_name: This is where the fun begins.

    Returns:
        The GDI file's contents.
    """
    tracks = random.randint(2, 20)
    line_end = "\n" if random.choice([0, 1]) else "\r\n"
    game_num = random.randint(1000, 9999)

    byte_index = 0
    lines = [str(tracks) + line_end]
    for track in range(1, tracks + 1):
        leading_spaces = " " * (len(str(tracks)) - len(str(track)))
        four_oh = 4 * (track % 2)
        ext = random.choices([".raw", ".bin"], [1, 3], k=1)[0]

        lines.append(
            f"{leading_spaces}{track} {byte_index} {four_oh} {game_num} "
            f'"{game_name}{ext}" 0{line_end}'
        )
        if track != tracks:
            byte_index = (byte_index << 1) + random.randint(0, 2**8)

    num_splitter_regex = re.compile(r"(\d+)")
    contents = ""
    for line in lines:
        # parts = [leading_spaces, track, space, byte_index, the_rest]
        parts = num_splitter_regex.split(line, maxsplit=2)
        # First line is a special case
        if parts[2] == line_end:
            contents += line
            continue
        digits = sum(char.isdigit() for char in parts[3])
        justify_spaces = " " * (len(str(byte_index)) - digits)
        line = parts[0] + parts[1] + parts[2] + justify_spaces + parts[3] + parts[4]
        contents += line
    return contents


def check_file_name(file: str, dirname: str) -> str:
    """Makes sure the output file name is correct.

    Args:
        file: The path to a file or a file name.
        dirname: The name of the directory the file is in.

    Returns:
        The file's extension if the file name passed inspection.
    """
    file_name = path.basename(file)
    name, ext = path.splitext(file_name)
    if ext.lower() == ".gdi":
        assert name == "disc"
        return ".gdi"
    if ext.lower() == ".raw" or ext.lower() == ".bin":
        assert name[:5] == "track"
        try:
            int(name[5:])
            if ext.lower() == ".raw":
                return ".raw"
            return ".bin"
        except ValueError:  # pragma: no cover
            assert False
    elif ext.lower() == ".txt":
        assert name == dirname
        return ".txt"
    else:  # pragma: no cover
        print("name was: " + name)
        assert False


def check_files(
    directory: str, expected_exts: List[str], whitelist: List[str] = None
) -> None:
    """Validates the file names in a dir.

    Args:
        directory: The path to a game's directory.
        expected_exts: The non-exclusive list of extensions to check.
        whitelist: Files that should not be checked.
    """
    whitelist = [] if whitelist is None else whitelist
    exts = dict.fromkeys(expected_exts, 0)
    dirname = path.basename(directory)
    with scandir(directory) as itr:
        for item in itr:
            if path.isfile(item):
                if item.name in whitelist:
                    continue
                ext = check_file_name(item.name, dirname)
                if ext in exts:
                    exts[ext] += 1
            elif path.isdir(item):
                continue
            else:  # pragma: no cover
                assert False

    for count in exts.values():
        assert count > 0
