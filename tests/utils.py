"""Functions used across various unit tests."""

from os import path, scandir
from typing import List, Tuple


def make_files(tmpdir: str, game_name: str) -> Tuple[str, List[str], List[str]]:
    """creates a typical game directory

    Args:
        tmpdir: A directory where the game files' directory will be made.
        game_name: What's this bad boy gonna be called?

    Returns:
        3-tuple:
        - The path to the game's directory
        - A list of filenames that were created
        - A list of file extensions that were created (used in some tests)
    """
    filenames = (
        game_name + ".gdi",
        game_name + "(track1).bin",
        game_name + "(track2).bin",
        game_name + "(track3).raw",
    )
    game_dir = tmpdir.mkdir(game_name)
    file_extensions = []
    for filename in filenames:
        file_path = game_dir.join(filename)
        file_path.write("")
        _1, ext = path.splitext(filename)
        if ext not in file_extensions:
            file_extensions.append(ext)

    return game_dir, filenames, file_extensions


def check_filename(file: str, dirname: str) -> str:
    """makes sure the output file name is correct

    Args:
        file: The path to a file or a filename.
        dirname: The name of the directory the file is in.

    Returns:
        The file's extension if the filename passed inspection.
    """
    filename = path.basename(file)
    name, ext = path.splitext(filename)
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
    """validates the filenames in a dir

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
                ext = check_filename(item.name, dirname)
                if ext in exts:
                    exts[ext] += 1
            elif path.isdir(item):
                continue
            else:  # pragma: no cover
                assert False

    for count in exts.values():
        assert count > 0
