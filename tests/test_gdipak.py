""" Tests for gdipak"""

import pytest
from os import path, scandir
from py import path as pypath

from utils import make_files, check_files
from gdipak import Gdipak
from argparser import RecursiveMode

class TestGetFilesInDir:
    def test_alphanumeric(self, tmpdir):
        dir_name = "gamedir"
        file_name = "aBcD1234.gdi"
        p = tmpdir.mkdir(dir_name).join(file_name)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) == 1)
        out_file_dir, out_file_name = path.split(files[0])
        assert(out_file_name == file_name)
        assert(out_file_dir == path.realpath(dir_path))

    def test_special_chars(self, tmpdir):
        dir_name = "gamedir 2! (The Redirening)"
        file_name = "123 !@#$%^&()~S{}[]-=_+'`.bin"
        p = tmpdir.mkdir(dir_name).join(file_name)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) == 1)
        out_file_dir, out_file_name = path.split(files[0])
        assert(out_file_name == file_name)
        assert(out_file_dir == path.realpath(dir_path))

    def test_unrelated_file(self, tmpdir):
        dir_name = "gamedirrrr"
        file_name = "Vacation Photo-1528.jpg"
        p = tmpdir.mkdir(dir_name).join(file_name)
        p.write("")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) == 0)

    def test_multi_files(self, tmpdir):
        dir_name = "gamedir"
        file_names = (
            "mygame.gdi",
            "mygame(track1).bin",
            "mygame(track2).bin",
            "mygame(track3).raw",
            "mygame.txt")
        tmp_dir = tmpdir.mkdir(dir_name)
        for f in file_names:
            p = tmp_dir.join(f)
            p.write("")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        files = g.get_files_in_dir(dir_path)
        assert(len(files) == (len(file_names) -1))
        for f in files:
            assert(f != file_names[len(file_names) - 1])

class TestGetSubdirsInDir:
    def test_dirs_dont_exist(self, tmpdir):
        tmpdir.mkdir("basedir")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        dirs = g.get_subdirs_in_dir(dir_path)
        assert(len(dirs) == 0)

    def test_dirs_exist(self, tmpdir):
        base = tmpdir.mkdir("basedir")
        sub1 = base.mkdir("subdir1")
        sub2 = base.mkdir("subdir2")
        dir_path = tmpdir.listdir()[0]
        g = Gdipak()
        dirs = g.get_subdirs_in_dir(dir_path)
        assert(len(dirs) == 2)
        assert(sub1 in dirs)
        assert(sub2 in dirs)

class TestWriteFile:
    def test_same_file(self, tmpdir):
        io_dir = tmpdir.mkdir("Game!")
        in_file = io_dir.join("Game!.gdi")
        contents = b"This is the contents of the file"
        in_file.write(contents)
        
        out_filename = path.join(io_dir, "disc.gdi")
        g = Gdipak()
        g.write_file(in_file.realpath(), out_filename)

        #original file nolonger exists
        assert(not in_file.check())
        with open(out_filename, "br") as f:
            assert(contents == f.read())

    def test_different_file(self, tmpdir):
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")
        
        out_dir = tmpdir.mkdir("outputdir")
        out_filename = path.join(out_dir, "disc.gdi")
        g = Gdipak()
        g.write_file(in_file.realpath(), out_filename)

        #original file still exists
        assert(in_file.check())
        with open(in_file, "br") as f_in:
            with open(out_filename, "br") as f_out:
                assert(f_in.read() == f_out.read())

    def test_missing_directory(self, tmpdir):
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")
        
        out_dir = path.join(tmpdir, "outputdir")
        out_filename = path.join(out_dir, "disc.gdi")
        g = Gdipak()
        g.write_file(in_file.realpath(), out_filename)

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
        g = Gdipak()
        g.write_name_file(out_dir, gdi_filename)
        assert(path.isfile(path.join(out_dir, game_name + ".txt")))

    def test_out_dir_exists_gdi_file_path(self, tmpdir):
        game_name = "Morgan the Bull And Stanley the Bear Go To Market"
        out_dir = tmpdir.mkdir(game_name)
        gdi_filepath = path.join(out_dir, game_name + ".gdi")
        g = Gdipak()
        g.write_name_file(out_dir, gdi_filepath)
        assert(path.isfile(path.join(out_dir, game_name + ".txt")))

    def test_out_dir_doesnt_exist_bare_gdi_file_str(self, tmpdir):
        game_name = "Somebody Once Told Me - Allstars!"
        out_dir = path.join(tmpdir, game_name)
        gdi_filename = game_name + ".gdi"
        g = Gdipak()
        g.write_name_file(out_dir, gdi_filename)
        assert(path.isfile(path.join(out_dir, game_name + ".txt")))

class TestPackGdi:
    def test_single_dir_same_out_dir(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        g = Gdipak()
        g.pack_gdi(dir_path, dir_path, False, False)

        #dir name didn't change
        assert(tmpdir.listdir()[0] == dir_path)
        check_files(dir_path, exts)

    def test_single_dir_same_out_dir_gen_namefile(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        g = Gdipak()
        g.pack_gdi(dir_path, dir_path, False, True)

        #dir name didn't change
        assert(tmpdir.listdir()[0] == dir_path)
        check_files(dir_path, exts)

    def test_single_dir_same_out_dir_default_args(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        g = Gdipak()
        g.pack_gdi(dir_path, dir_path)

        #dir name didn't change
        assert(tmpdir.listdir()[0] == dir_path) 
        check_files(dir_path, exts)

    def test_single_dir_different_out_dir(self, tmpdir):
        in_dir, in_filenames, exts = make_files(tmpdir, "mygame")
        out_dir = tmpdir.mkdir("processed_game")
        g = Gdipak()
        g.pack_gdi(in_dir, out_dir)

        #src files didn't change
        with scandir(in_dir) as itr: 
            for item in itr:
                assert(path.basename(item) in in_filenames)
        dir_path = path.join(out_dir, path.basename(in_dir))
        check_files(dir_path, exts)

    def test_recursive_dir_bad_recursive_mode(self, tmpdir):
        dir_path, _1, _2 = make_files(tmpdir, "mygame")
        make_files(dir_path, "some other game")
        out_dir = tmpdir.mkdir("output")
        g = Gdipak()
        with pytest.raises(ValueError):
            g.pack_gdi(dir_path, out_dir, "strawberry", False)

    def test_recursive_dir_same_out_dir_mode_none(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        make_files(dir_path, "some other game")
        g = Gdipak()
        g.pack_gdi(dir_path, dir_path, None, False)
        check_files(dir_path, exts)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    # subdir was not touched
                    with pytest.raises(AssertionError):
                        check_files(item, exts)
    
    def test_recursive_dir_same_out_dir_mode_zero(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        make_files(dir_path, "some other game")
        g = Gdipak()
        g.pack_gdi(dir_path, dir_path, RecursiveMode.PRESERVE_STRUCTURE, False)
        check_files(dir_path, exts)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    check_files(item, exts)

    def test_recursive_dir_same_out_dir_mode_one(self, tmpdir):
        dir_path, _1, exts = make_files(tmpdir, "mygame")
        make_files(dir_path, "some other game")
        g = Gdipak()
        # mode is changed implicitly due to in_dir == out_dir
        g.pack_gdi(dir_path, dir_path, RecursiveMode.FLAT_STRUCTURE, False)
        check_files(dir_path, exts)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    check_files(item, exts)

    def test_recursive_dir_different_out_dir_mode_one(self, tmpdir):
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        g = Gdipak()
        g.pack_gdi(sg_dir, out_dir, RecursiveMode.FLAT_STRUCTURE)

        dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(dir_path, sg_exts)
        dir_path = path.join(out_dir, path.basename(sog_dir))
        check_files(dir_path, sog_exts)
        dir_path = path.join(out_dir, path.basename(soog_dir))
        check_files(dir_path, soog_exts)
        dir_path = path.join(out_dir, path.basename(sooog_dir))
        check_files(dir_path, sooog_exts)

    def test_recursive_dir_different_out_dir_mode_zero(self, tmpdir):
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        g = Gdipak()
        g.pack_gdi(sg_dir, out_dir, RecursiveMode.PRESERVE_STRUCTURE)

        sg_dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(sg_dir_path, sg_exts)
        sog_dir_path = path.join(sg_dir_path, path.basename(sog_dir))
        check_files(sog_dir_path, sog_exts)
        soog_dir_path = path.join(sg_dir_path, path.basename(soog_dir))
        check_files(soog_dir_path, soog_exts)
        sooog_dir_path = path.join(soog_dir_path, path.basename(sooog_dir))
        check_files(sooog_dir_path, sooog_exts)

    def test_missing_gdi_file(self, tmpdir):
        name = "mygame"
        dir_path, _1, _2 = make_files(tmpdir, name)
        gdi_path = pypath.local(path.join(dir_path, name + ".gdi"))
        gdi_path.remove()
        g = Gdipak()
        with pytest.raises(ValueError):
            g.pack_gdi(dir_path, dir_path)

    def test_too_many_gdi_files(self, tmpdir):
        name = "mygame"
        dir_path, _1, _2 = make_files(tmpdir, name)
        f = dir_path.join("who put this file here.gdi")
        f.write("")
        g = Gdipak()
        with pytest.raises(ValueError):
            g.pack_gdi(dir_path, dir_path)
