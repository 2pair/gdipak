"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

from sys import argv
from argparser import ArgParser
from gdipak import Gdipak

__version__ = 0.1


def main():
    """Normal execution when run as script"""
    arg_parser = ArgParser(__version__)
    args = arg_parser.run(argv[1:])

    in_dir = args["in_dir"]
    recursive = args["recursive"]
    namefile = args["namefile"]
    modify = args["modify"]
    out_dir = str()
    if not modify:
        out_dir = args["out_dir"]
    else:
        out_dir = in_dir

    gdipak = Gdipak()
    gdipak.pack_gdi(in_dir, out_dir, recursive, namefile, modify)


if __name__ == "__main__":
    main()  # pragma: no cover
