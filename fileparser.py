"""Parses files that are part of the GDI package and generates 
new files that are expected by the SD card maker program"""

import re
from os import path
from tempfile import mkstemp

class FileParser:
    valid_extensions = (".gdi", ".bin", ".raw")
    # This regex takes any string of characters that contains "track" and a number and captures the track number
    filename_regex = re.compile(r"^[\s\S]*track[\s\S]*?([\d]+)", re.IGNORECASE)
    # This regex takes any bin or raw file between double quotes and captures the track number
    gdi_file_ref_regex = re.compile(r"\"[\s\S]*?track[\s\S]*?([\d]+)[\s\S]*?\.(?:bin)|(?:raw)\"", re.IGNORECASE)

    @classmethod
    def parse_file(FileParser, file_path):
        """ Based on the input filetype performs the required type of parsing
        arguments:  
            file_path    str    A string representing the path to a file, with extension
        returns:         tuple(str str)    The name of the final output file and the location 
                                           on disk where the file's contents are stored. This 
                                           may be a temporary directory or the original file's location.
        raises:          ValueError, SyntaxError
        """
        _1, ext = path.splitext(file_path)
        if ext == ".gdi":
            return (FileParser.convert_filename(file_path), FileParser.process_gdi(file_path))
        elif ext in FileParser.valid_extensions:
            return (FileParser.convert_filename(file_path), file_path)
        else:
            raise ValueError("Invalid file type")


    @classmethod
    def process_gdi(FileParser, gdi_file):
        """ processes the contents of the gdi file to sanitize track names and remove white space
        to comply with SD card maker expectations
        arguments:  
            gdi_file     str    A string representing the path to a gdi filename, with extension
        returns:         str    A string representing the path to the processed file contents. This
                                is a temporary file. The original file is not modified.
        raises:          ValueError, SyntaxError
        """
        tmp_file, tmp_path = mkstemp()
        with open(gdi_file, 'r') as f_gdi:
            with open(tmp_file, "w") as f_tmp:
                for line in f_gdi:
                    #TODO: process the line.
                    f_tmp.write(line)
     
                return tmp_path


    @classmethod
    def convert_filename(FileParser, file_path):
        """ Based on the input filename generates an output filename
        arguments:  
            file_path    str    A string representing a path to a file, with extension
        returns:         str    A string that GDEMU expects for that file's name
        raises:          ValueError, SyntaxError
        """
        file_dir, file_name = path.split(file_path)
        name, ext = path.splitext(file_name)
        ext = ext.lower()
        if not ext or ext not in FileParser.valid_extensions:
            raise ValueError("Invalid file type")
        if ext == ".gdi":
            return "disc.gdi"
        result = FileParser.filename_regex.match(name)
        if not result:
            raise SyntaxError("Filename does not contain track information")
        track_num = str(int(result.group(1))) # removes leading zeros
        return path.join(file_dir, "track" + track_num.zfill(2) + ext)
