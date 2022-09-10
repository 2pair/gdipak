"""Constructs argument parsing class and validates arguments"""

import enum
from pathlib import Path
from sys import exit as sys_exit

from argparse import ArgumentParser


@enum.unique
class RecursiveMode(enum.Enum):
    """Enum for the output format when working on a directory recursively."""

    # The output directories will mirror the input directories. ex:
    # ./in/good_games/game_a -> ./out/good_games/game_a
    # ./in/bad_games/game_b -> ./out/bad_games/game_b
    PRESERVE_STRUCTURE = 0
    # The output directories will all be moved into the out directory. ex:
    # ./in/good_games/game_a -> ./out/game_a
    # ./in/bad_games/game_b -> ./out/game_b
    FLATTEN_STRUCTURE = 1


@enum.unique
class OperatingMode(enum.Enum):
    """Enum for the type of action the program performs."""

    # In copy mode the input files are not modified, new files are created.
    COPY = "COPY"
    # In move mode the input files are moved to the output directory and then modified.
    MODIFY = "MODIFY"


class ArgParser:
    """Processes CLI arguments."""

    # pylint: disable=too-few-public-methods

    def __init__(self, version: str) -> None:
        """Setup argument parser.

        Args:
          version: The program version, to be used in command line help.
        """
        self.version = version

    def __call__(self, args: list) -> dict:
        """Setups up the argument parsing and returns the validated arguments.

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
            args:  A dictionary of args from argparse.

        Returns:
            dict: A dictionary of the args modified to enforce rules.
        """
        try:
            error_str = "Input directory is not a directory"
            if not Path(args["in_dir"]).is_dir():
                print(error_str)
                sys_exit(0)
        except TypeError:
            print(error_str)
            sys_exit(0)

        if args["out_dir"] == "in-dir":
            args["out_dir"] = args["in_dir"]
        try:
            error_str = "Output directory is not a directory."
            if not Path(args["out_dir"]).is_dir():
                print()
                sys_exit(0)
        except TypeError:
            print(error_str)
            sys_exit(0)

        args["mode"] = OperatingMode(args["mode"])

        if args["recursive"] is not None:
            args["recursive"] = RecursiveMode(args["recursive"])

        return args

    def __setup(self) -> ArgumentParser:
        """Creates the argument parser.

        Args:
            None

        Returns:
            argparse.ArgumentParser
        """

        parser = ArgumentParser(
            description="""Scans a directory and optionally subdirectories for *.gdi
            files and the related *.bin files. creates new file names that conform
            to the expected format for the GDEMU.

            NOTE: If the 'recursive' argument is NOT given, it is assumed that 'in-dir'
            contains the files for one game. In this case the output files will be
            written directly to the 'out-dir'. if the 'recursive' argument IS given, it
            is assumed that the 'in-dir' DOES NOT contain files for a game but instead
            contains a sub directory for each game."""
        )
        parser.add_argument(
            "-v", "--version", action="version", version=str(self.version)
        )

        parser.add_argument(
            "-i",
            "--in-dir",
            action="store",
            dest="in_dir",
            required=True,
            help="The directory to scan for *.gdi files for processing.",
            metavar="ROOT_SEARCH_DIRECTORY",
        )
        parser.add_argument(
            "-o",
            "--out-dir",
            action="store",
            dest="out_dir",
            required=True,
            help="""the directory to output results to. This can be set to 'in-dir' as a
                shortcut if it is desired that the 'out-dir' be the same as the
                'in-dir'.""",
            metavar="OUTPUT_DIRECTORY",
        )
        parser.add_argument(
            "-m",
            "--mode",
            action="store",
            choices=("COPY", "MODIFY"),
            type=str.upper,
            dest="mode",
            required=True,
            help="""Chooses the mode of operation. In 'COPY' mode The original files
                will not be moved, modified, or deleted. In 'MODIFY' mode the input
                files will be moved to the output directory and then edited in
                place. Note that 'COPY' mode will use roughly 2x the initial disk
                space.""",
        )
        parser.add_argument(
            "-r",
            "--recursive",
            action="store",
            choices=(0, 1),
            nargs="?",
            type=int,
            const=0,
            dest="recursive",
            required=False,
            help="""If specified will search within subdirectories. Valid values are
                blank, 0 and 1. In mode 0 the input directory structure is preserved in
                the output directory. In mode 1 each game output directory is created
                as an immediate sub-directory of the output directory. If no value is
                specified mode 0 is used.""",
            metavar="MODE",
        )
        parser.add_argument(
            "-n",
            "--name-file",
            action="store_true",
            dest="namefile",
            required=False,
            help="""If specified will create a *.txt file with the original name of the
            *.gdi file""",
        )

        return parser
