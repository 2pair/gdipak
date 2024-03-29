"""Functions used across various unit tests."""

from collections import namedtuple
from os import path
from pathlib import Path
import random
import re
from typing import Dict, List, Tuple


# pylint: disable=too-few-public-methods
class GdiGenerator:
    """Creates the contents of a GDI file as it is before being converted."""

    MetaData = namedtuple(
        "MetaData", "name num_tracks game_num offsets extensions line_end"
    )

    split_on_nums_regex = re.compile(r"(\d+)")

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        game_name: str,
        track_exts: List[str] = None,
        track_offsets: List[int] = None,
        game_num: int = None,
        line_end: str = None,
    ) -> None:
        """Args:
        game_name: This is where the fun begins.
        track_exts: Optional. A list of extensions to use for the tracks. The
          extensions should be provided without the dot separator.
        track_offsets: Optional. A list of track byte offsets. If left as None track
         count and track offsets will be random. The length should be equal to the
         length of the track_exts list.
        game_num: Optional. The special number assigned to this game. If left None
          game num will be random.
        line_end: Optional.What to use as the line ending. Should be one of \n or
          \r\n. If left None line ending will be random.
        """
        self.game_name = game_name
        self.track_exts = track_exts
        self.track_offsets = track_offsets
        self.game_num = game_num
        self.line_end = line_end

    def __call__(self) -> Tuple[str, Dict]:
        """Generate a new GDI file.
        If some parameters are not set, random ones will be generated.

        Returns:
            The GDI file's contents and a metadata dict.
        """
        track_exts = self.track_exts
        if track_exts is None:
            num_tracks = random.randint(2, 20)
        else:
            num_tracks = len(track_exts)
        track_offsets = self.track_offsets
        if not track_offsets:
            track_offsets = []
            byte_offset = 0
            for _ in range(num_tracks):
                track_offsets.append(byte_offset)
                byte_offset = self._byte_offset_generator(byte_offset)
        if not track_exts:
            track_exts = []
            for _ in range(num_tracks):
                track_exts.append(random.choices(["raw", "bin"], [1, 3], k=1)[0])
        game_num = self.game_num if self.game_num else random.randint(1000, 9999)
        line_end = self.line_end
        if not line_end:
            line_end = "\n" if random.choice([0, 1]) else "\r\n"

        return (
            self._make_gdi_contents(
                self.game_name, track_offsets, track_exts, game_num, line_end
            ),
            self.MetaData(
                self.game_name,
                num_tracks,
                game_num,
                track_offsets,
                track_exts,
                line_end,
            ),
        )

    @staticmethod
    def _byte_offset_generator(byte_offset):
        """Makes a number that is bigger than the previous number."""
        return (byte_offset << 1) + random.randint(0, 2**8)

    # pylint: disable=too-many-arguments, too-many-locals
    @classmethod
    def _make_gdi_contents(
        cls,
        game_name: str,
        track_offsets: List[int],
        track_exts: List[str],
        game_num: int,
        line_end: str,
    ) -> str:
        """Creates the contents of a GDI file as it is before being converted.

        Args:
            game_name: This is where the fun begins.
            track_sizes: A list of track sizes.
            track_exts: A list of extensions to use for each track.
            game_num: The special number assigned to this game.
            line_end: What to use as the line ending.

        Returns:
            The GDI file's contents.
        """
        track_count = len(track_offsets)
        base_lines = [str(track_count) + line_end]
        for track_index, track_offset in enumerate(track_offsets):
            index = track_index + 1
            leading_spaces = " " * (len(str(track_count)) - len(str(index)))
            four_oh = 4 * (index % 2)

            base_lines.append(
                f"{leading_spaces}{index} {track_offset} {four_oh} {game_num} "
                f'"{game_name} (Track {index}).{track_exts[track_index]}" 0{line_end}'
            )

        contents = ""
        for index, line in enumerate(base_lines):
            # First line is a special case
            if index == 0:
                contents += line
                continue
            LineParts = namedtuple(
                "LineParts",
                ["leading_spaces", "track_num", "space", "byte_index", "remainder"],
            )
            line_parts = LineParts(*cls.split_on_nums_regex.split(line, maxsplit=2))
            digits = sum(char.isdigit() for char in line_parts.byte_index)
            justify_spaces = " " * (len(str(track_offsets[-1])) - digits)
            line = (
                line_parts.leading_spaces
                + line_parts.track_num
                + line_parts.space
                + justify_spaces
                + line_parts.byte_index
                + line_parts.remainder
            )
            contents += line
        return contents


def make_files(tmp_path: Path, game_name: str) -> Tuple[Path, List[str], List[str]]:
    """Creates a typical game directory.

    Args:
        tmp_path: A Path representing a directory where the game files' directory
          will be made.
        game_name: What's this bad boy gonna be called?

    Returns:
        3-tuple:
        - The path to the game's directory
        - A list of file names that were created
        - A list of file extensions that were created (used in some tests)
    """
    file_names = [
        game_name + "(track1).bin",
        game_name + "(track2).bin",
        game_name + "(track3).raw",
    ]
    game_dir = tmp_path / game_name
    game_dir.mkdir()
    file_extensions = []
    for file_name in file_names:
        file_path = game_dir / file_name
        file_path.touch()
        _1, ext = path.splitext(file_name)
        file_extensions.append(ext)

    dotless_exts = [ext[1:] for ext in file_extensions]
    contents, _ = GdiGenerator(game_name, track_exts=dotless_exts)()
    gdi_file = game_dir / (game_name + ".gdi")
    gdi_file.write_text(contents, encoding="UTF-8")
    file_names.append(str(gdi_file.name))
    file_extensions.append(gdi_file.suffix)

    return game_dir, file_names, file_extensions


def check_file_name(file: str, dirname: str) -> str | None:
    """Makes sure the output file name is correct.

    Args:
        file: The path to a file or a file name.
        dirname: The name of the directory the file is in.

    Returns:
        The file's extension if the file name passed inspection.
    """
    file_name = path.basename(file)
    name, ext = path.splitext(file_name)
    if ext == "":
        assert name == dirname
        return None
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
        except ValueError as ex:  # pragma: no cover
            # file was a raw or bin but didn't have a number after "track"
            raise AssertionError from ex
    else:
        # Unknown extension
        raise AssertionError


def check_files(
    directory: Path, expected_exts: List[str], whitelist: List[str] = None
) -> None:
    """Validates the file names in a dir.

    Args:
        directory: The path to a game's directory.
        expected_exts: The non-exclusive list of extensions to check.
        whitelist: Files that should not be checked.
    """
    whitelist = [] if whitelist is None else whitelist
    exts = dict.fromkeys(expected_exts, 0)
    for item in directory.iterdir():
        if item.is_file():
            if item.name in whitelist:
                continue
            ext = check_file_name(item.name, directory.name)
            if ext in exts:
                exts[ext] += 1
        elif item.is_dir():
            continue
        else:
            # Item is not a file or directory
            raise AssertionError

    for count in exts.values():
        assert count > 0


GameData = namedtuple("GameData", "name extensions in_files")
"""Contains the information necessary to verify a processed game matches the input."""


def check_games(
    games_data: List[GameData], base_path: Path, fail_on_non_dirs: bool = True
) -> None:
    """Verifies all games in a directory.
    All games should be in their own directories within the directory pointed to by
    base_path.

    Args:
        games_data: List of game data.
        base_path: The directory in which
        fail_on_non_dirs: Whether or not files in the base_path is a fail condition."""
    found_count = 0
    for subdir in base_path.iterdir():
        if not subdir.is_dir():
            if fail_on_non_dirs:
                raise AssertionError
            continue
        for game_data in games_data:
            if subdir.name != game_data.name:
                continue
            check_files(
                directory=subdir,
                expected_exts=game_data.extensions,
                whitelist=game_data.in_files,
            )
            found_count += 1
            break
        else:
            # directory name was not a game name
            raise AssertionError
    assert len(games_data) == found_count


def create_dirs_in_dir(
    base_dir: Path, count: int, start_index: int = 0, prefix: str = "subdir"
):
    """Creates the given number of directories within a base directory.
    Directories will be named f"{prefix}{index}" where index begins at start_index. If
    start count is 1 the index will be omitted.

    Args:
        base_dir: The directory in which the other directories are created.
        count: The number of directories to make.
        start_index: the first number used in directory names.
        prefix: A string used in the directory name.
    """
    subdirs = []
    for i in range(count):
        subdir = base_dir / f"{prefix}{(start_index + i) if count > 1 else ''}"
        subdir.mkdir()
        subdirs.append(str(subdir))
    return subdirs
