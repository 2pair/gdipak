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

    def write_file(self, input_file, output_file):
        """ Generates a file with the given contents
        arguments:  input_file: a path to a file from which to copy data 
        output_file: a path to which to write the data
        returns: None
        """
        in_dir = os.path.dirname(input_file)
        out_dir = os.path.dirname(output_file)
        if in_dir == out_dir:
            os.rename(input_file, output_file)
        else:
            with open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())


    def convert_filename(self, input_filename):
        """ Based on the input filename generates an output filename
        arguments:  A string representing a filename, with extension
        returns:    A string that GDEMU expects for that file's name
        """
        name, ext = os.path.splitext(input_filename)
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
        arguments:  A path-like object for a directory to search in
        returns:    A  list of file names or None if no files found
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


def validate_args(args):
    """ Validates the supplied arguments. Exits on failure
    arguments:  A dictionary of args from argparse
    returns:    None
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
    arguments:  None
    returns:    An instance of argparse.ArgumentParser"""

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
    #modify_files = True
    out_dir = str()
    if "modify" not in args.keys():
        #modify_files = False
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    g = gdipak()
    files = g.get_files_in_dir(in_dir)
    for in_file in files:
        in_filename = os.path.basename(in_file)
        out_filename = g.convert_filename(in_filename)
        out_path = os.path.join(out_dir, out_filename)
        g.write_file(in_file, out_file)


if __name__ == "__main__":
    main()
