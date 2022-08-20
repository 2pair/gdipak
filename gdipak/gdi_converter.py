"""GDI File conversion class"""
from os import path, remove
import re

from gdipak.file_processor import FileProcessor


class GdiConverter:
    """Converts the GDI file into the format SD Card Maker wants."""

    remove_repeated_spaces_regex = re.compile(r" +", " ")

    def __init__(self, file_path: str) -> None:
        """
        Args:
            file_path: The path to file.
        """
        self.file_path = path.realpath(file_path)
        self.backup_file_path = file_path + ".bak"
        self.backup_exists = False

    def convert_file(self) -> None:
        """Converts the file in place.

        This method also creates a backup of the file then deletes it when the
        conversion is finished so that users don't meet with a terrible fate.
        """
        with open(self.file_path, "r+", encoding="UTF-8") as file:
            contents = file.readlines()
            self._backup_file(contents)
            contents = self.convert_file_contents(contents)
            file.seek(0)
            file.truncate()
            file.writelines(contents)
            self._delete_backup()

    @classmethod
    def convert_file_contents(cls, file_contents: str) -> str:
        """Converts the file contents.

        Args:
            file_contents: A string containing all of the contents of the file. These
            files are short, so reading in the whole thing isn't a big deal.
        """
        file_contents = cls._replace_file_names(file_contents)
        file_contents = cls._remove_extra_whitespace(file_contents)
        return file_contents

    def _backup_file(self, contents: str) -> None:
        """Creates a backup of the file on disk.

        Args:
            contents: the contents of the file.
        """
        with open(self.backup_file_path, "w", encoding="UTF-8") as b_file:
            b_file.writelines(contents)

    def _delete_backup(self) -> None:
        """Removes the backup of the file from the disk."""
        if not self.backup_exists:
            return
        if path.exists(self.backup_file_path):
            remove(self.backup_file_path)
            self.backup_exists = False

    @classmethod
    def _remove_extra_whitespace(cls, file_contents: str) -> str:
        """Removes extra spaces from the file.

        ex:
        ' 2    600 0 2252 "MyGame (USA) (Track 2).bin" 0'
        becomes:
        '2 600 0 2252 "MyGame (USA) (Track 2).bin" 0'

        Args:
            file_contents: All the text from the GDI file.

        Returns:
            str: The modified contents of the GDI file.
        """
        file_contents = cls.remove_repeated_spaces_regex.sub(re.escape(file_contents))
        if file_contents[0] == " ":
            file_contents = file_contents[1:]
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
            str: The modified contents of the GDI file.
        """
        output_contents = ""
        lines = file_contents.splitlines()
        for index, line in enumerate(lines):
            start_quote_index = line.find('"')
            end_quote_index = line.rfind('"')
            # Line without a file name
            if start_quote_index == -1 and end_quote_index == -1:
                continue
            # Invalid Line
            if start_quote_index == -1 or end_quote_index == -1:
                raise ValueError(
                    f"Line {index + 1} only contains a single quote, file names "
                    "should be between two quotes."
                )

            file_name = line[start_quote_index:end_quote_index]
            new_file_name = FileProcessor.convert_file_name(re.escape(file_name))
            line, replacements = re.subn(file_name, new_file_name, line)
            if not replacements:
                raise ValueError("The filename was not found!")
            output_contents += line

        return output_contents
