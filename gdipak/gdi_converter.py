"""GDI File conversion class"""
from pathlib import Path
import re

from gdipak.file_utils import convert_file_name


class GdiConverter:
    """Converts the GDI file into the format SD Card Maker expects."""

    repeated_spaces_regex = re.compile(r" +")
    repeated_tabs_regex = re.compile(r"\t+")

    def __init__(self, file_path: str | Path = None, file_contents: str = None) -> None:
        """Accepts either file_path or file_contents, not both.

        Args:
            file_path: The path to file.
            file_contents: The contents of the file.
        """
        if not file_path and not file_contents:
            raise ValueError("Either file_path or file_contents must be defined.")
        if file_path and file_contents:
            raise ValueError("Only one of file_path or file_contents can be defined.")
        self.file_contents = file_contents
        self.file_path = Path(file_path) if file_path else None
        self.backup_file_path = (
            Path(str(self.file_path) + ".bak") if self.file_path else None
        )
        self.backup_exists = False

    def convert_file(self) -> None:
        """Converts the file in place.

        This method also creates a backup of the file then deletes it when the
        conversion is finished so that users don't meet with a terrible fate.
        """
        if not self.file_path:
            raise ValueError("Cannot convert file, file_path is None")
        with self.file_path.open(mode="r+", encoding="UTF-8") as file:
            contents = file.read()
            self._backup_file(contents)
            contents = self.convert_file_contents(contents)
            file.seek(0)
            file.truncate()
            file.writelines(contents)
            self._delete_backup()

    def convert_file_contents(self, file_contents: str = None) -> str:
        """Converts the file contents.

        Args:
            file_contents: A string containing all of the contents of the file. These
                files are short, so reading in the whole thing isn't a big deal. If set
                to None, use the file_contents passed on during instantiation.
        Returns:
            The converted file contents.
        """
        if not file_contents:
            file_contents = self.file_contents
        if not file_contents:
            raise ValueError(
                "file_contents should be a string representing the "
                "contents of a GDI file"
            )
        file_contents = self._replace_file_names(file_contents)
        file_contents = self._remove_extra_whitespace(file_contents)
        return file_contents

    def _backup_file(self, contents: str) -> None:
        """Creates a backup of the file on disk.

        Args:
            contents: the contents of the file.
        """
        with self.backup_file_path.open(mode="w", encoding="UTF-8") as backup_file:
            backup_file.writelines(contents)
        self.backup_exists = True

    def _delete_backup(self) -> None:
        """Removes the backup of the file from the disk."""
        if not self.backup_exists:
            return
        self.backup_file_path.unlink(missing_ok=True)
        self.backup_exists = False

    @classmethod
    def _remove_extra_whitespace(cls, file_contents: str) -> str:
        """Removes extra spaces and tabs from the file.

        ex:
        ' 2    600 0 2252 "MyGame (USA) (Track 2).bin" 0'
        becomes:
        '2 600 0 2252 "MyGame (USA) (Track 2).bin" 0'

        Args:
            file_contents: All the text from the GDI file.

        Returns:
            The modified contents of the GDI file.
        """
        file_contents = cls.repeated_tabs_regex.sub(
            " ", file_contents.replace("\\", r"\\")
        )
        file_contents = cls.repeated_spaces_regex.sub(" ", file_contents)
        lines = file_contents.splitlines(True)
        for index, line in enumerate(lines):
            if line[0] == " ":
                lines[index] = line[1:]
        file_contents = "".join(line for line in lines)
        return file_contents

    @classmethod
    def _replace_file_names(cls, file_contents: str) -> str:
        """Replaces the original file names with the new file names.

        ex:
        '2 600 0 2252 "MyGame (USA) (Track 2).bin" 0'
        becomes:
        '2 600 0 2252 "track02.bin" 0'

        Args:
            file_contents: All the text from the GDI file.

        Returns:
            The modified contents of the GDI file.
        """
        output_contents = ""
        lines = file_contents.splitlines(True)
        for index, line in enumerate(lines):
            if index == 0:
                output_contents += line  # First line holds track count
                continue
            start_quote_index = line.find('"')
            end_quote_index = line.rfind('"')
            # Line without a file name
            if start_quote_index == -1 and end_quote_index == -1:
                raise ValueError(
                    f"Line {index + 1} does not reference a quoted file name."
                )
            # Invalid Line
            if start_quote_index == end_quote_index:
                raise ValueError(
                    f"Line {index + 1} only contains a single quote, file names "
                    "should be between two quotes."
                )
            start_quote_index += 1
            file_name = line[start_quote_index:end_quote_index]
            new_file_name = convert_file_name(file_name)
            line = re.sub(re.escape(file_name), new_file_name, line)
            output_contents += line

        return output_contents
