"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

from sys import argv
from gdipak.arg_parser import ArgParser, OperatingMode
from gdipak.file_utils import get_sub_dirs_in_dir
from gdipak.packer import CopyPacker, MovePacker

__version__ = 0.1


def main():
    """Normal execution when run as script."""
    arg_parser = ArgParser(__version__)
    args = arg_parser(argv[1:])

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
        game_dirs.append(get_sub_dirs_in_dir(in_dir))

    for game_dir in game_dirs:
        # TODO: if recursive is preserve need to do out_dir=out_dir_in / (game_dir - in_dir)
        # TODO: if recursive is flatten need to do out_dir=out_dir_in / game_dir.name
        packer = packer_class(in_dir=game_dir, out_dir=out_dir)
        packer.package_game(create_name_file=namefile)

if __name__ == "__main__":
    main()  # pragma: no cover
