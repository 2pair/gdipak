"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

from sys import argv
from gdipak.arg_parser import ArgParser
from gdipak import gdipak

__version__ = 0.1


def main():
    """Normal execution when run as script."""
    arg_parser = ArgParser(__version__)
    args = arg_parser(argv[1:])

    in_dir = args["in_dir"]
    recursive = args["recursive"]
    namefile = args["namefile"]
    modify = args["modify"]
    if not modify:
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    gdipak.pack_gdi(in_dir, out_dir, recursive, namefile, modify)


if __name__ == "__main__":
    main()  # pragma: no cover
