"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""
from abc import ABC, abstractmethod
from pathlib import Path

from gdipak import file_utils
from gdipak.gdi_converter import GdiConverter


class BasePacker(ABC):
    """Repackages all of the game files in the format needed for the SD card maker."""

    def __init__(self, in_dir: str | Path, out_dir: str | Path) -> None:
        """Saves paths to all of the input files and the output path."""
        self.out_dir = Path(out_dir)
        self.game_files = file_utils.get_game_files_in_dir(in_dir)

        gdi_files = [file for file in self.game_files if file.suffix == ".gdi"]
        if len(gdi_files) < 1:
            raise ValueError("Directory does not contain a gdi file")
        if len(gdi_files) > 1:
            raise ValueError("Directory contains more than one gdi file")
        self.gdi_file = gdi_files[0]

    @abstractmethod
    def file_action(self, in_file: str | Path, out_file: str | Path) -> None:
        """The action to take on the file (move or copy).

        Args:
            in_file: The source file.
            out_file: The destination file.
        """
        raise NotImplementedError

    def package_game(self, *, create_name_file: bool = False) -> None:
        """Performs specific action (move or copy) on all input files to create the
        output files.

        Args:
            create_name_file: If True, a name file will also be created."""
        for in_file in self.game_files:
            out_file = self.out_dir / file_utils.convert_file_name(in_file)
            self.file_action(in_file, out_file)
            # in_file can no longer be used, could be gone.
            if out_file.suffix == ".gdi":
                GdiConverter(out_file).convert_file()
        if create_name_file:
            file_utils.write_name_file(self.out_dir, self.gdi_file)


class MovePacker(BasePacker):
    """Moves or renames (if in_dir == out_dir) the source files and packages them."""

    def file_action(self, in_file: str | Path, out_file: str | Path) -> None:
        """Moves the in file to the out file location.
        In file will no longer exist.

        Args:
            in_file: The source file.
            out_file: The destination file.
        """
        Path(in_file).replace(out_file)


class CopyPacker(BasePacker):
    """Copies the source files and packages them."""

    def file_action(self, in_file: str | Path, out_file: str | Path) -> None:
        """Copies the in file contents to the out file location.
        In file will not be modified.

        Args:
            in_file: The source file.
            out_file: The destination file.
        """
        file_utils.write_file(in_file, out_file)
