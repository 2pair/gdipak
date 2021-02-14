"""What is this and what does it do"""

__version__ = 1.0

import argparse
import re

""" Creates the argument parser
    arguments: None
    returns: an instance of argparse.ArgumentParser"""
def __setup_argparser():
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


"""Normal execution when run as script"""
def main():
    parser = __setup_argparser()
    args = vars(parser.parse_args())

    input_dir = args["in_dir"]
    recursive = args["recursive"]
    modify_files = True
    output_dir = input_dir
    if "modify" not in args:
        modify_files = False
        output_dir = args["out_dir"]


if __name__ == "__main__":
    main()
