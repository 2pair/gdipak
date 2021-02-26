""" Tests for gdipak"""

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

class TestGetFilesInDir:
    def test_alphanumeric(self, tmpdir):
        dirname = "gamedir"
        filename = "aBcD1234.gdi"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 1)
        assert(files[0] == filename)

    def test_special_chars(self, tmpdir):
        dirname = "gamedir 2! (The Redirening)"
        filename = "123 !@#$%^&()~S{}[]-=_+'`.bin"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 1)
        assert(files[0] == filename)

    def test_unrelated_file(self, tmpdir):
        dirname = "gamedirrrr"
        filename = "Vacation Photo-1528.jpg"
        p = tmpdir.mkdir(dirname).join(filename)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) is 0)

    def test_multi_files(self, tmpdir):
        dirname = "gamedir"
        filenames = (
            "mygame.gdi",
            "mygame(track1).bin",
            "mygame(track2).bin",
            "mygame(track3).raw",
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

class TestGetSubdirsInDir:
    def test_dirs_dont_exist(self, tmpdir):
        tmpdir.mkdir("basedir")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        dirs = g.get_subdirs_in_dir(dir_path)
        assert(len(dirs) is 0)

    def test_dirs_exist(self, tmpdir):
        base = tmpdir.mkdir("basedir")
        sub1 = base.mkdir("subdir1")
        sub2 = base.mkdir("subdir2")
        dir_path = tmpdir.listdir()[0]
        g = gdipak()
        dirs = g.get_subdirs_in_dir(dir_path)
        assert(len(dirs) is 2)
        assert(sub1 in dirs)
        assert(sub2 in dirs)

class TestConvertFilename:
    def test_convert_gdi(self):
        g = gdipak()
        result = g.convert_filename("Very Good Game ~PAL~.gdi")
        assert(result == "disc.gdi")

    def test_convert_tracks(self):
        g = gdipak()
        result = g.convert_filename("Very Good Game (Track 1) PAL.raw")
        assert(result == "track01.raw")

        result = g.convert_filename("track racing game 2-track5-(region and language information).bin")
        assert(result == "track05.bin")

        result = g.convert_filename("_THE_GAME_TRACK_4_.bin")
        assert(result == "track04.bin")

        result = g.convert_filename("Sometimes.People.Do.This.Track.12.raw")
        assert(result == "track12.raw")

    def test_bad_file_type(self):
        g = gdipak()
        with pytest.raises(ValueError):
            g.convert_filename("Very Good Game.cdi")

    def test_ambiguous_file_name(self):
        g = gdipak()
        with pytest.raises(SyntaxError):
            g.convert_filename("Very Good Game.bin")

class TestWriteFile:
    def test_same_file(self, tmpdir):
        io_dir = tmpdir.mkdir("Game!")
        in_file = io_dir.join("Game!.gdi")
        contents = b"This is the contents of the file"
        in_file.write(contents)
        
        out_filename = os.path.join(io_dir, "disc.gdi")
        g = gdipak()
        g.write_file(in_file, out_filename)

        #original file nolonger exists
        assert(not in_file.check())
        with open(out_filename, "br") as f:
            assert(contents == f.read())

    def test_different_file(self, tmpdir):
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")
        
        out_dir = tmpdir.mkdir("outputdir")
        out_filename = os.path.join(out_dir, "disc.gdi")
        g = gdipak()
        g.write_file(in_file, out_filename)

        #original file still exists
        assert(in_file.check())
        with open(in_file, "br") as f_in:
            with open(out_filename, "br") as f_out:
                assert(f_in.read() == f_out.read())

    def test_missing_directory(self, tmpdir):
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")
        
        out_dir = os.path.join(tmpdir, "outputdir")
        out_filename = os.path.join(out_dir, "disc.gdi")
        g = gdipak()
        g.write_file(in_file, out_filename)

        #original file still exists
        assert(in_file.check())
        with open(in_file, "br") as f_in:
            with open(out_filename, "br") as f_out:
                assert(f_in.read() == f_out.read())

class TestWriteNameFile:
    def test_out_dir_exists_bare_gdi_file_str(self, tmpdir):
        game_name = "Bills Okay But Lonely Adventure- The Game"
        out_dir = tmpdir.mkdir(game_name)
        gdi_filename = game_name + ".gdi"
        g = gdipak()
        g.write_name_file(out_dir, gdi_filename)
        assert(os.path.isfile(os.path.join(out_dir, game_name + ".txt")))

    def test_out_dir_exists_gdi_file_path(self, tmpdir):
        game_name = "Morgan the Bull And Stanley the Bear Go To Market"
        out_dir = tmpdir.mkdir(game_name)
        gdi_filepath = os.path.join(out_dir, game_name + ".gdi")
        g = gdipak()
        g.write_name_file(out_dir, gdi_filepath)
        assert(os.path.isfile(os.path.join(out_dir, game_name + ".txt")))

    def test_out_dir_doesnt_exist_bare_gdi_file_str(self, tmpdir):
        game_name = "Somebody Once Told Me - Allstars!"
        out_dir = os.path.join(tmpdir, game_name)
        gdi_filename = game_name + ".gdi"
        g = gdipak()
        g.write_name_file(out_dir, gdi_filename)
        assert(os.path.isfile(os.path.join(out_dir, game_name + ".txt")))

class TestProcessDir:
    def test_single_dir_same_out_dir(self, tmpdir):
        assert(True)

    def test_single_dir_different_out_dir(self, tmpdir):
        assert(True)

    def test_recursive_dir_same_out_dir(self, tmpdir):
        assert(True)

    def test_recursive_dir_different_out_dir(self, tmpdir):
        assert(True)

    def test_missing_gdi_file(self, tmpdir):
        assert(True)

    def test_too_many_gdi_files(self, tmpdir):
        assert(True)
