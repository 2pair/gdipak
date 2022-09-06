"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

from sys import argv
from gdipak.arg_parser import ArgParser
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
    modify = args["modify"]
    # TODO: This doesn't make sense, change it to a move argument.
    # default will be copying file
    out_dir = args["out_dir"]
    if modify:
        packer_class = MovePacker
    else:
        packer_class = CopyPacker

    dirs = [in_dir]
    if recursive:
        dirs.append(get_sub_dirs_in_dir(in_dir))
    packer = packer_class(in_dir=in_dir, out_dir=out_dir)
    packer.package_game(create_name_file=namefile)

    # TODO: This was moved from gdipak.py, broken for now
    # if recursive:
    #    subdirs = in_dir
    #    for subdir in subdirs:
    #        if modify_files:
    #            sub_out_dir = subdir
    #        elif recursive == RecursiveMode.FLATTEN_STRUCTURE:
    #            sub_out_dir = out_dir
    #        elif recursive == RecursiveMode.PRESERVE_STRUCTURE:
    #            sub_out_dir = os.path.join(out_dir, last_dir)
    #        else:
    #            raise ValueError(
    #                """Argument 'recursive' is not a member of the enum
    #                'RecursiveMode'"""
    #            )


if __name__ == "__main__":
    main()  # pragma: no cover
