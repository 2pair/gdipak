"""What is this and what does it do"""

__version__ = 0.1

import argparse
import os
import sys
import fnmatch
import re

class gdipak:
    """ Performs the stuff which do"""

    def get_files_in_dir(self, directory):
        """ Searches in a given directory for files relevent to the gdi format
        arguments:  A directory to search in
        returns:    A  list of file names or None if no files found
        """
        files = list()
        with os.scandir(directory) as itr:
            for item in itr:
                if not item.is_file():
                    continue
                if fnmatch.fnmatch(item.name, "*.gdi"):
                    files.append(item.name)
                if fnmatch.fnmatch(item.name, "*.bin"):
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

    input_dir = args["in_dir"]
    recursive = args["recursive"]
    modify_files = True
    output_dir = input_dir
    if "modify" not in args.keys():
        modify_files = False
        output_dir = args["out_dir"]

    g = gdipak()
    g.get_files(input_dir)

if __name__ == "__main__":
    main()
