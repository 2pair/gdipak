"""Parses files that are part of the GDI package and generates
new files that are expected by the SD card maker program"""

from pathlib import Path
import re


# TODO: This doesn't need to be a class anymore. just move the function and regex to
# utils
class FileProcessor:
    """Parses and converts files into a format required by the SD card maker."""

    valid_extensions = (".gdi", ".bin", ".raw")
    # This regex takes any string of characters that contains "track" and a
    # number and captures the track number
    file_name_regex = re.compile(
        r"^[\s\S]*track[\s\S]*?([\d]+)",
        re.IGNORECASE,
    )
    # This regex takes any bin or raw file between double quotes and captures
    # the track number
    gdi_file_ref_regex = re.compile(
        r"\"[\s\S]*?track[\s\S]*?([\d]+)[\s\S]*?\.(?:bin)|(?:raw)\"", re.IGNORECASE
    )

    @classmethod
    def convert_file_name(cls, file_path: str | Path) -> str:
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
        if not ext or ext not in cls.valid_extensions:
            raise ValueError("Invalid file type")
        if ext == ".gdi":
            return "disc.gdi"
        result = cls.file_name_regex.match(name)
        if not result:
            raise SyntaxError("File name does not contain track information")
        track_num = str(int(result.group(1)))  # removes leading zeros
        return "track" + track_num.zfill(2) + ext
        # return path.join(file_dir, "track" + track_num.zfill(2) + ext)
