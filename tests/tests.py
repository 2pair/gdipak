""" Tests for gdipak

"""

import pytest
from gdipak import *

from os import path

class TestValidateArgs:
    def test_current_dir(self):
        args = dict([("in_dir", "."), ("out_dir", ".")])
        validate_args(args)

    def test_parent_dir(self):
        args = dict([("in_dir", ".."), ("out_dir", "..")])
        validate_args(args)

    def test_fully_qualified_dir(self):
        fqd = path.abspath(".")
        args = dict([("in_dir", fqd), ("out_dir", fqd)])
        validate_args(args)

class TestFileOperations:
    def test_get_files_in_dir_alphanumeric(self, tmpdir):
        dirname = "gamedir"
        filename = "aBcD1234.gdi"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 1)
        assert(files[0] == filename)
        

    def test_get_files_in_dir_special_chars(self, tmpdir):
        dirname = "gamedir 2! (The Redirening)"
        filename = "123 !@#$%^&*()<>?{}[]-=_+.bin"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 1)
        assert(files[0] == filename)

    def test_get_files_in_dir_unrelated_file(self, tmpdir):
        dirname = "gamedirrrr"
        filename = "Vacation Photo-1528.jpg"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 0)

    def test_get_files_in_dir_multi_files(self, tmpdir):
        dirname = "gamedir"
        filenames = (
            "mygame.gdi",
            "mygame(track1).bin",
            "mygame(track2).bin",
            "mygame(track3).bin",
            "mygame.txt")
        tmp_dir = tmpdir.mkdir(dirname)
        for f in filenames:
            p = tmp_dir.join(f)
            p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is (len(filenames) -1))
        for f in files:
            assert(f != filenames[len(filenames) - 1])
