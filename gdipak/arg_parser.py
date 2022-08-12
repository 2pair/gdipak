"""Constructs argument parsing class and validates arguments"""
import sys
import os
import enum

from argparse import ArgumentParser


@enum.unique
class RecursiveMode(enum.Enum):
    """Enum for the output format when working on a directory recursively"""

    PRESERVE_STRUCTURE = 0
    FLATTEN_STRUCTURE = 1


# pylint disable=too-few-public-methods
class ArgParser:
    """Processes CLI arguments"""

    def __init__(self, version: str) -> None:
        """Setup argument parser.

        Args:
          version: The program version, to be used in command line help
        """
        self.version = version

    def __call__(self, args: list) -> dict:
        """setups up the argument parsing and returns the validated arguments

        Args:
            args: The arguments from the command line, as represented by sys.argv.

        Returns:
            dict: the dictionary of validated arguments
        """
        parser = self.__setup()
        args = vars(parser.parse_args(args))
        args = self.__validate_args(args)
        return args

    def __validate_args(self, args: dict) -> dict:
        """Validates and sanitizes the supplied arguments. Exits on failure.

        Args:
            args:  A dictionary of args from argparse

        Returns:
            dict: A dictionary of the args modified to enforce rules
        """
        fail_msg = "Input directory is not a directory"
        # mandatory argument
        if args["in_dir"] is None:
            print(fail_msg)
            sys.exit(0)

        if not os.path.isdir(args["in_dir"]):
            print(fail_msg)
            sys.exit(0)

        if args["out_dir"] is None and args["modify"] is None:
            print("Neither output directory nor modify option was specified")
            sys.exit(0)
        elif args["out_dir"] is not None:
            if not os.path.isdir(args["out_dir"]):
                print("Output directory is not a directory")
                sys.exit(0)

        # if we are modifying the files we must use preserve structure recursive mode
        if args["modify"] is True:
            args["recursive"] = RecursiveMode.PRESERVE_STRUCTURE
        elif args["recursive"] is not None:
            fail_msg = 'valid values for "recursive" are blank, 0, and 1.'
            r_mode = args["recursive"]
            if r_mode not in (0, 1):
                print(fail_msg)
                sys.exit(0)
            args["recursive"] = RecursiveMode(r_mode)

        return args

    def __setup(self) -> ArgumentParser:
        """Creates the argument parser

        Args:
            None

        Returns:
            argparse.ArgumentParser
        """

        parser = ArgumentParser(
            description="""Scans a directory and optionally subdirectories for *.gdi
            files and the related *.bin files. creates new file names that conform
            to the expected format for the GDEMU"""
        )
        parser.add_argument(
            "-v", "--version", action="version", version=str(self.version)
        )

        parser.add_argument(
            "-i",
            "--indirectory",
            action="store",
            dest="in_dir",
            required=True,
            help="The directory to scan for *.gdi files for processing",
            metavar="ROOT_SEARCH_DIRECTORY",
        )
        parser.add_argument(
            "-r",
            "--recursive",
            action="store",
            nargs="?",
            type=int,
            const=0,
            dest="recursive",
            required=False,
            help="""If specified will search within subdirectories. Valid values are
                blank, 0 and 1. In mode 0 directory structure is preserved in the
                output directory. In mode 1 each game output directory is created
                in a flat directory. If no value is specified or --modify is specified
                mode 0 is used.""",
            metavar="MODE",
        )
        parser.add_argument(
            "-n",
            "--namefile",
            action="store_true",
            dest="namefile",
            required=False,
            help="""If specified will create a *.txt file with the original name of the
            *.gdi file""",
        )

        out_group = parser.add_mutually_exclusive_group(required=True)
        out_group.add_argument(
            "-m",
            "--modify",
            action="store_true",
            dest="modify",
            required=False,
            help="""If specified will modify files in place, otherwise
                files will be copied with new names to the output directory""",
        )
        out_group.add_argument(
            "-o",
            "--outdirectory",
            action="store",
            dest="out_dir",
            required=False,
            help="the directory to output results to",
            metavar="OUTPUT_DIRECTORY",
        )

        return parser
