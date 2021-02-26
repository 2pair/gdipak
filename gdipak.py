"""Parses GDI formatted game dumps and formats them for
consumption by GDEMU"""

__version__ = 0.1

import argparse
import os
import sys
import fnmatch
import re

class gdipak:
    """Includes functions for finding and parsing files that are 
    part of a .gdi game dump"""
    valid_extensions = (".gdi", ".bin", ".raw")

    def process_dir(self, in_dir, out_dir, recursive=False, namefile=False):
        """ converts and copies or renames all files in a directory 
        and optionally subdirectories.
        arguments: 
            in_dir      str     The directory to process
            out_dir     str     The output directory
            recursive   bool    If subdirectories should be processed
            namefile    bool    Should a name file be generated
        returns:        None
        raises:         ValueError
        """
        files = self.get_files_in_dir(in_dir)
        gdi_files = [match for match in files if ".gdi" in match]
        if len(gdi_files) > 1:
            raise ValueError("Directory does not contain a gdi file")
        if len(gdi_files) > 1:
            raise ValueError("Directory contains more than one gdi file")

        if namefile:
            self.write_name_file(out_dir, gdi_files[0])

        for in_file in files:
            in_filename = os.path.basename(in_file)
            out_filename = self.convert_filename(in_filename)
            out_file = os.path.join(out_dir, out_filename)
            self.write_file(in_file, out_file)

        if recursive:
            subdirs = self.get_subdirs_in_dir(in_dir)
            for subdir in subdirs:
                sub_outdir = str()
                if in_dir == out_dir:
                    sub_outdir = subdir
                else:
                    sub_outdir = os.path.join(out_dir, subdir)
                self.process_dir(subdir, sub_outdir, recursive)


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


def validate_args(args):
    """ Validates the supplied arguments. Exits on failure
    arguments:  
        args        dict(str, str)  A dictionary of args from argparse
    returns:        None
    raises:         None
    """
    if args["in_dir"] is not None:
        fail_msg = "Input directory is not a directory"
        try:
            if not os.path.isdir(args["in_dir"]):
                print(fail_msg)
                sys.exit(0)
        except FileNotFoundError:
            print(fail_msg)
            sys.exit(0)

    if args["out_dir"] is not None:
        fail_msg = "Output directory is not a directory"
        try:
            if not os.path.isdir(args["out_dir"]):
                print(fail_msg)
                sys.exit(0)
        except FileNotFoundError:
            print(fail_msg)
            sys.exit(0)


def setup_argparser():
    """ Creates the argument parser
    arguments:      None
    returns:        argparse.ArgumentParser
    raises:         None
    """

    parser = argparse.ArgumentParser(description=
        """Scans a directory and optionally subdirectories for *.gdi files 
        and the related *.bin files. creates new file names that conform 
        to the expected format for the GDEMU""")
    parser.add_argument("-v", "--version", 
        action="version", 
        version=str(__version__))

    parser.add_argument("-d", "--indirectory",
        action="store",
        dest="in_dir",
        required=True,
        help="The directory to scan for *.gdi files for processing",
        metavar="ROOT_SEARCH_DIRECTORY")
    parser.add_argument("-r", "--recursive",
        action="store_true",
        dest="recursive",
        required=False,
        help="If specified will search within subdirectories")
    parser.add_argument("-n", "--namefile",
        action="store_true",
        dest="namefile",
        required=False,
        help="""If specified will create a *.txt file with the original name of the *.gdi file""")

    out_group = parser.add_mutually_exclusive_group(required=True)
    out_group.add_argument("-m", "--modify",
        action="store_true",
        dest="modify",
        required=False,
        help="""If specified will modify files in place, otherwise 
            files will be copied with new names to the output directory""")
    out_group.add_argument("-o", "--outdirectory",
        action="store",
        dest="out_dir",
        required=False,
        help="the directory to output results to",
        metavar="OUTPUT_DIRECTORY")
    
    return parser


def main():
    """Normal execution when run as script"""

    parser = setup_argparser()
    args = vars(parser.parse_args())
    validate_args(args)

    in_dir = args["in_dir"]
    recursive = args["recursive"]
    namefile = args["namefile"]
    out_dir = str()
    if "modify" not in args.keys():
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    g = gdipak()
    g.process_dir(in_dir, out_dir, recursive, namefile)


if __name__ == "__main__":
    main()
