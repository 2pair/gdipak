"""Parses GDI formatted game dumps and formats them for
consumption by GDEMU"""

__version__ = 0.1

from argparser import ArgParser, RecursiveMode
from sys import argv
import os
import fnmatch
import re

class Gdipak:
    """Includes functions for finding and parsing files that are 
    part of a .gdi game dump"""
    valid_extensions = (".gdi", ".bin", ".raw")
    
    def pack_gdi(self, in_dir, out_dir, recursive=None, namefile=False):
        """ converts and copies or renames all files in a directory 
        and optionally subdirectories. If indir == out_dir files will be modified.
        arguments: 
            in_dir      str             The directory to process
            out_dir     str             The output directory
            recursive   RecursiveMode   If subdirectories should be processed
            namefile    bool            Should a name file be generated
        returns:        None
        raises:         ValueError
        """
        files = self.get_files_in_dir(in_dir)
        gdi_files = fnmatch.filter(files, "*.gdi")
        if len(gdi_files) < 1:
            raise ValueError("Directory does not contain a gdi file")
        if len(gdi_files) > 1:
            raise ValueError("Directory contains more than one gdi file")

        if namefile:
            self.write_name_file(out_dir, gdi_files[0])

        last_dir = os.path.basename(in_dir)
        for in_file in files:
            in_filename = os.path.basename(in_file)
            out_filename = self.convert_filename(in_filename)
            in_file = os.path.join(in_dir, in_filename)
            out_file = out_dir
            if in_dir != out_dir:
                out_file = os.path.join(out_file, last_dir)
            out_file = os.path.join(out_file, out_filename)
            self.write_file(in_file, out_file)

        if recursive:
            subdirs = self.get_subdirs_in_dir(in_dir)
            for subdir in subdirs:
                sub_outdir = str()
                # in_dir == out_dir means modify files
                if in_dir == out_dir:
                    sub_outdir = subdir
                elif recursive == RecursiveMode.FLAT_STRUCTURE:
                    sub_outdir = out_dir
                elif recursive == RecursiveMode.PRESERVE_STRUCTURE:
                    sub_outdir = os.path.join(out_dir, last_dir)
                else:
                    raise ValueError("Argument 'recursive' is not a mmeber of the enum 'RecursiveMode'")
                self.pack_gdi(subdir, sub_outdir, recursive)


    def write_name_file(self, out_dir, gdi_file):
        """ Creates an empty text file with the name of the given gdi file
        arguments: 
            out_dir     str     The location to write the name file
            gdi_file    str     The file who's name will be used for the name file
        returns:        None
        raises:         None
        """
        if not os.path.exists(out_dir):
            os.makedirs(os.path.realpath(out_dir))
        
        gdi_filename = os.path.basename(gdi_file)
        filename = os.path.splitext(gdi_filename)[0]
        txt_filename = filename + ".txt"
        out_file = os.path.join(out_dir, txt_filename)
        with open(out_file, 'w') as f_out:
            f_out.write("")
        

    def write_file(self, in_file, out_file):
        """ Generates a file with the given contents
        arguments:  
            in_file     str    a path to a file from which to copy data 
            out_file    str    a path to which to write the data
        returns:        None
        raises:         None
        """
        in_dir = os.path.dirname(in_file)
        out_dir = os.path.dirname(out_file)
        if in_dir == out_dir:
            os.rename(in_file, out_file)
        else:
            if not os.path.exists(out_dir):
                os.makedirs(os.path.realpath(out_dir))
            with open(in_file, 'rb') as f_in:
                with open(out_file, 'wb') as f_out:
                    f_out.write(f_in.read())


    def convert_filename(self, in_filename):
        """ Based on the input filename generates an output filename
        arguments:  
            in_filename  str    A string representing a filename, with extension
        returns:         str    A string that GDEMU expects for that file's name
        raises:          ValueError, SyntaxError
        """
        name, ext = os.path.splitext(in_filename)
        ext = ext.lower()
        if not ext or ext not in self.valid_extensions:
            raise ValueError("Invalid file type")
        if ext == ".gdi":
            return "disc.gdi"
        regex = re.compile(r"^[\s\S]*track[\s\S]*?([\d]+)", re.IGNORECASE)
        result = regex.match(name)
        if not result:
            raise SyntaxError("Filename does not contain track information")
        return "track" + result.group(1).zfill(2) + ext


    def get_files_in_dir(self, directory):
        """ Searches in a given directory for files relevent to the gdi format
        arguments:  
            directory   str     A path-like object for a directory to search in
        returns:        str     A  list of file names or None if no files found
        raises:         None
        """
        files = list()
        with os.scandir(directory) as itr:
            for item in itr:
                if not item.is_file():
                    continue
                for ext in self.valid_extensions:
                    if fnmatch.fnmatch(item.name, "*" + ext):
                        files.append(item.name)
        return files


    def get_subdirs_in_dir(self, directory):
        """ Searches in a given directory for subdirectories
        arguments:  
            directory:  str         A path-like object for a directory to search in
        returns:        list(str)   A  list of subdirectories or None if none are found
        raises:         None
        """
        dirs = list()
        with os.scandir(directory) as itr:
            for item in itr:
                if not item.is_dir():
                    continue
                dirs.append(item.path)
        return dirs


def main():
    """Normal execution when run as script"""
    a = ArgParser(__version__)
    args = a.run(argv[1:])

    in_dir = args["in_dir"]
    recursive = args["recursive"]
    namefile = args["namefile"]
    out_dir = str()
    if not args["modify"]:
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    g = Gdipak()
    g.pack_gdi(in_dir, out_dir, recursive, namefile)


if __name__ == "__main__":
    main()  # pragma: no cover
