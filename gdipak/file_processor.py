"""Parses files that are part of the GDI package and generates
new files that are expected by the SD card maker program"""

import re
from os import path
from tempfile import mkstemp


class FileProcessor:
    """Parses and converts files into a format required by the SD card maker."""

    valid_extensions = (".gdi", ".bin", ".raw")
    # This regex takes any string of characters that contains "track" and a
    # number and captures the track number
    filename_regex = re.compile(
        r"^[\s\S]*track[\s\S]*?([\d]+)",
        re.IGNORECASE,
    )
    # This regex takes any bin or raw file between double quotes and captures
    # the track number
    gdi_file_ref_regex = re.compile(
        r"\"[\s\S]*?track[\s\S]*?([\d]+)[\s\S]*?\.(?:bin)|(?:raw)\"", re.IGNORECASE
    )

    @classmethod
    def get_output_file_contents(cls, file_path: str) -> str:
        """Based on the input filetype performs the required type of parsing.

        Args:
            file_path (str): A string representing the path to a file, with extension

        Returns:
            str: The location on disk where the file's contents are stored. This may be
                 a temporary directory or the original file's location.

        Raises:
            ValueError, SyntaxError
        """
        _1, ext = path.splitext(file_path)
        if ext == ".gdi":
            return path.realpath(cls.process_gdi(file_path))
        if ext in cls.valid_extensions:
            return path.realpath(file_path)
        raise ValueError("Invalid file type")

    @classmethod
    def process_gdi(cls, gdi_file: str) -> str:
        """processes the contents of the gdi file to sanitize track names and remove
        white space to comply with SD card maker expectations

        Args:
            gdi_file (str): A string representing the path to a gdi filename, with
                            extension
        Returns:
            str: A string representing the path to the processed file contents. This
                 is a temporary file. The original file is not modified.
        Raises:
            ValueError, SyntaxError
        """
        tmp_file, tmp_path = mkstemp()
        with open(gdi_file, "r", encoding="UTF-8") as f_gdi:
            with open(tmp_file, "w", encoding="UTF-8") as f_tmp:
                for line in f_gdi:
                    # TODO: process the line.
                    f_tmp.write(line)

                return tmp_path

    @classmethod
    def convert_filename(cls, file_path: str) -> str:
        """Based on the input filename, generates an output filename
        arguments:
            file_path (str): A string representing a path to a file, with extension
        returns:
            str: A string that GDEMU expects for that file's name
        raises:
            ValueError, SyntaxError
        """
        file_dir, file_name = path.split(file_path)
        name, ext = path.splitext(file_name)
        ext = ext.lower()
        if not ext or ext not in cls.valid_extensions:
            raise ValueError("Invalid file type")
        if ext == ".gdi":
            return "disc.gdi"
        result = cls.filename_regex.match(name)
        if not result:
            raise SyntaxError("Filename does not contain track information")
        track_num = str(int(result.group(1)))  # removes leading zeros
        return path.join(file_dir, "track" + track_num.zfill(2) + ext)
