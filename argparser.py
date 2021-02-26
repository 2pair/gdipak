
import argparse
import sys
import os

from gdipak import __version__

class ArgParser:
    def run(self):
        """ setups up the argument parsing and returns the validated arguments
        arguments:  None
        returns:    dict(str, str)  the dictionary of validated arguments
        raises:     None"""
        parser = self.__setup_argparser()
        args = vars(parser.parse_args())
        self.__validate_args(args)
        return args


    def __validate_args(self, args):
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


    def __setup_argparser(self):
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