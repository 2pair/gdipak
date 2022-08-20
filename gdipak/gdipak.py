"""Parses GDI formatted game dumps and formats them for
consumption by the Madsheep SD card maker for GDEMU"""

import fnmatch
import os
from typing import List

from gdipak.arg_parser import RecursiveMode
from gdipak.file_processor import FileProcessor


# TODO: Reduce complexity
def pack_gdi(  # noqa: C901
    in_dir: str,
    out_dir: str,
    recursive: RecursiveMode = None,
    namefile: bool = False,
    modify_files: bool = False,
) -> None:
    """converts and copies or renames all files in a directory
    and optionally subdirectories.

    Args:
        in_dir: The directory to process
        out_dir: The output directory
        recursive: If subdirectories should be processed
        namefile: Should a name file be generated
        modify_files: If the files in the input directory should be modified.
          If in_dir == out_dir the files will be modified in the same directory.
          If in_dir != out_dir the files will first be moved to the output
            directory, then modified.

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
        out_file_path = FileProcessor.convert_file_name(in_file)
        out_file_name = os.path.basename(out_file_path)
        out_file_contents = FileProcessor.get_output_file_contents(in_file)

        out_file = out_dir
        if in_dir != out_dir:
            out_file = os.path.join(out_file, last_dir)
        out_file = os.path.join(out_file, out_file_name)

        if modify_files:
            os.rename(in_file, out_file_path)

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


def write_name_file(out_dir: str, gdi_file: str) -> None:
    """Creates an empty text file with the name of the given gdi file

    Args:
        out_dir: The location to write the name file
        gdi_file: The file who's name will be used for the name file

    Returns:
        None

    Raises:
        None
    """
    if not os.path.exists(out_dir):
        os.makedirs(os.path.realpath(out_dir))

    gdi_file_name = os.path.basename(gdi_file)
    file_name = os.path.splitext(gdi_file_name)[0]
    txt_file_name = file_name + ".txt"
    out_file = os.path.join(out_dir, txt_file_name)
    with open(out_file, "w", encoding="UTF-8") as f_out:
        f_out.write("")


def write_file(in_file: str, out_file: str) -> None:
    """Generates a file with the given contents

    Args:
        in_file: a path to a file from which to copy data
        out_file: a path to which to write the data

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


def get_files_in_dir(directory: str) -> List[str]:
    """Searches in a given directory for files relevant to the gdi format

    Args:
        directory: A path-like object for a directory to search in

    Returns:
        A  list of file paths.

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


def get_subdirs_in_dir(directory: str, max_recursion: int = None) -> List[str]:
    """Searches in a given directory for subdirectories

    Args:
        directory: A path-like object for a directory to search in
        max:recursion: The number of times to look in sub-directories for more
          directories.

    Returns:
        A  list of subdirectories.

    Raises:
        None
    """
    dirs = []
    with os.scandir(directory) as itr:
        for item in itr:
            if not item.is_dir():
                continue
            dirs.append(item.path)
            if max_recursion != 0:
                if max_recursion is not None:
                    max_recursion -= 1
                sub_dirs = get_subdirs_in_dir(item.path, max_recursion)
                dirs.extend(sub_dirs)

    return dirs
