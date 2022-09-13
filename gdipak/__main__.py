"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

from sys import argv
from typing import List
from gdipak.arg_parser import ArgParser, OperatingMode
from gdipak.file_utils import get_subdirs_in_dir, transpose_path
from gdipak.packer import CopyPacker, MovePacker

__version__ = 0.1


def main(args: List[str] = None):
    """Normal execution when run as script.

    Args:
        args: List of command line arguments.
    """
    args = argv if args is None else args
    arg_parser = ArgParser(__version__)
    args = arg_parser(args[1:])

    in_dir = args["in_dir"]
    recursive = args["recursive"]
    namefile = args["namefile"]
    mode = args["mode"]
    out_dir = args["out_dir"]
    if mode == OperatingMode.MODIFY:
        packer_class = MovePacker
    else:
        packer_class = CopyPacker

    game_dirs = []
    if recursive is None:
        game_dirs.append(in_dir)
    elif recursive is not None:
        game_dirs.extend(get_subdirs_in_dir(in_dir))

    for game_dir in game_dirs:
        if recursive is None:
            game_out_dir = out_dir
        else:
            game_out_dir = transpose_path(game_dir, in_dir, out_dir, recursive)
        packer = packer_class(in_dir=game_dir, out_dir=game_out_dir)
        packer.package_game(create_name_file=namefile)


if __name__ == "__main__":
    main()  # pragma: no cover
