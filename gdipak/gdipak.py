"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

import fnmatch
import os

from gdipak.arg_parser import RecursiveMode
from gdipak.file_processor import FileProcessor


# TODO: Reduce complexity
def pack_gdi(  # noqa: C901
    in_dir, out_dir, recursive=None, namefile=False, modify_files=False
):
    """converts and copies or renames all files in a directory
    and optionally subdirectories. If in_dir == out_dir files will be modified.

    Args:
        in_dir (str): The directory to process
        out_dir (str): The output directory
        recursive (RecursiveMode): If subdirectories should be processed
        namefile (bool): Should a name file be generated
        modify_files (bool): If the files in the input directory should be modified

    Returns:
        None

    Raises:
        ValueError, SyntaxError
    """
    files = get_files_in_dir(in_dir)
    gdi_files = fnmatch.filter(files, "*.gdi")
    if len(gdi_files) < 1:
        raise ValueError("Directory does not contain a gdi file")
    if len(gdi_files) > 1:
        raise ValueError("Directory contains more than one gdi file")
    gdi_file = gdi_files[0]

    last_dir = os.path.basename(in_dir)
    if namefile:
        write_name_file(os.path.join(out_dir, last_dir), gdi_file)

    for in_file in files:
        out_filename = FileProcessor.convert_filename(in_file)
        out_file_contents = FileProcessor.get_output_file_contents(in_file)

        out_file = out_dir
        if in_dir != out_dir:
            out_file = os.path.join(out_file, last_dir)
        out_file = os.path.join(out_file, out_filename)

        if modify_files:
            os.rename(in_file, out_filename)

        write_file(out_file_contents, out_file)

    if recursive:
        subdirs = get_subdirs_in_dir(in_dir)
        for subdir in subdirs:
            if modify_files:
                sub_out_dir = subdir
            elif recursive == RecursiveMode.FLATTEN_STRUCTURE:
                sub_out_dir = out_dir
            elif recursive == RecursiveMode.PRESERVE_STRUCTURE:
                sub_out_dir = os.path.join(out_dir, last_dir)
            else:
                raise ValueError(
                    """Argument 'recursive' is not a member of the enum
                    'RecursiveMode'"""
                )
            pack_gdi(subdir, sub_out_dir, recursive, namefile)


def write_name_file(out_dir, gdi_file):
    """Creates an empty text file with the name of the given gdi file

    Args:
        out_dir (str): The location to write the name file
        gdi_file (str): The file who's name will be used for the name file

    Returns:
        None

    Raises:
        None
    """
    if not os.path.exists(out_dir):
        os.makedirs(os.path.realpath(out_dir))

    gdi_filename = os.path.basename(gdi_file)
    filename = os.path.splitext(gdi_filename)[0]
    txt_filename = filename + ".txt"
    out_file = os.path.join(out_dir, txt_filename)
    with open(out_file, "w", encoding="UTF-8") as f_out:
        f_out.write("")


def write_file(in_file, out_file):
    """Generates a file with the given contents

    Args:
        in_file (str): a path to a file from which to copy data
        out_file (str): a path to which to write the data

    Returns:
        None

    Raises:
        None
    """
    if in_file == out_file:
        return

    out_dir = os.path.dirname(out_file)
    if not os.path.exists(out_dir):
        os.makedirs(os.path.realpath(out_dir))
    with open(in_file, "rb") as f_in:
        with open(out_file, "wb") as f_out:
            f_out.write(f_in.read())


def get_files_in_dir(directory):
    """Searches in a given directory for files relevant to the gdi format

    Args:
        directory (str): A path-like object for a directory to search in

    Returns:
        (list(str)):   A  list of file paths or None if no files found

    Raises:
        None
    """
    files = []
    with os.scandir(directory) as itr:
        for item in itr:
            if not item.is_file():
                continue
            for ext in FileProcessor.valid_extensions:
                if fnmatch.fnmatch(item.name, "*" + ext):
                    files.append(item.path)
    return files


def get_subdirs_in_dir(directory):
    """Searches in a given directory for subdirectories

    Args:
        directory (str): A path-like object for a directory to search in

    Returns:
        (list(str)): A  list of subdirectories or None if none are found

    Raises:
        None
    """
    dirs = []
    with os.scandir(directory) as itr:
        for item in itr:
            if not item.is_dir():
                continue
            dirs.append(item.path)
    return dirs
