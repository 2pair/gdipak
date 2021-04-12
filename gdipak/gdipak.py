"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

__version__ = 0.1

from gdipak.argparser import ArgParser, RecursiveMode
from gdipak.fileparser import FileParser
from sys import argv
import os
import fnmatch

class Gdipak:
    """Includes functions for finding and parsing files that are 
    part of a .gdi game dump"""
    
    def pack_gdi(self, in_dir, out_dir, recursive=None, namefile=False, modify_files=False):
        """ converts and copies or renames all files in a directory 
        and optionally subdirectories. If indir == out_dir files will be modified.
        arguments: 
            in_dir          str             The directory to process
            out_dir         str             The output directory
            recursive       RecursiveMode   If subdirectories should be processed
            namefile        bool            Should a name file be generated
            modify_files    bool            If the files in the input directory should be modified
        returns:        None
        raises:         ValueError, SyntaxError
        """
        files = self.get_files_in_dir(in_dir)
        gdi_files = fnmatch.filter(files, "*.gdi")
        if len(gdi_files) < 1:
            raise ValueError("Directory does not contain a gdi file")
        if len(gdi_files) > 1:
            raise ValueError("Directory contains more than one gdi file")
        gdi_file = gdi_files[0]

        last_dir = os.path.basename(in_dir)
        if namefile:
            self.write_name_file(os.path.join(out_dir, last_dir), gdi_file)

        for in_file in files:
            out_filename = FileParser.convert_filename(in_file)
            out_file_contents = FileParser.get_output_file_contents(in_file)

            out_file = out_dir
            if in_dir != out_dir:
                out_file = os.path.join(out_file, last_dir)
            out_file = os.path.join(out_file, out_filename)

            if modify_files:
                os.rename(in_file, out_filename)

            self.write_file(out_file_contents, out_file)

        if recursive:
            subdirs = self.get_subdirs_in_dir(in_dir)
            for subdir in subdirs:
                sub_outdir = str()
                if modify_files:
                    sub_outdir = subdir
                elif recursive == RecursiveMode.FLAT_STRUCTURE:
                    sub_outdir = out_dir
                elif recursive == RecursiveMode.PRESERVE_STRUCTURE:
                    sub_outdir = os.path.join(out_dir, last_dir)
                else:
                    raise ValueError("Argument 'recursive' is not a member of the enum 'RecursiveMode'")
                self.pack_gdi(subdir, sub_outdir, recursive, namefile)


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
        if in_file == out_file:
            return

        out_dir = os.path.dirname(out_file)
        if not os.path.exists(out_dir):
            os.makedirs(os.path.realpath(out_dir))
        with open(in_file, 'rb') as f_in:
            with open(out_file, 'wb') as f_out:
                f_out.write(f_in.read())


    def get_files_in_dir(self, directory):
        """ Searches in a given directory for files relevent to the gdi format
        arguments:  
            directory   str         A path-like object for a directory to search in
        returns:        list(str)   A  list of file paths or None if no files found
        raises:         None
        """
        files = list()
        with os.scandir(directory) as itr:
            for item in itr:
                if not item.is_file():
                    continue
                for ext in FileParser.valid_extensions:
                    if fnmatch.fnmatch(item.name, "*" + ext):
                        files.append(item.path)
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
    modify = args["modify"]
    out_dir = str()
    if not modify:
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    g = Gdipak()
    g.pack_gdi(in_dir, out_dir, recursive, namefile, modify)


if __name__ == "__main__":
    main()  # pragma: no cover
