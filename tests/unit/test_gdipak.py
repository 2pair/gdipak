""" Tests for gdipak"""

from os import path, scandir
from pathlib import Path
import pytest

from tests.utils import make_files, check_files
from gdipak import gdipak
from gdipak.arg_parser import RecursiveMode


class TestGetFilesInDir:
    """Tests getting a list of all the files in the directory."""

    def test_alphanumeric(self, tmp_path):
        """Test a directory and file with only alphanumeric characters."""
        dir_name = "gamedir"
        file_name = "aBcD1234.gdi"
        tmp_path = tmp_path / dir_name
        tmp_path.mkdir()
        (tmp_path / file_name).touch()
        files = gdipak.get_files_in_dir(tmp_path)
        assert len(files) == 1
        out_file_dir, out_file_name = path.split(files[0])
        assert out_file_name == file_name
        assert out_file_dir == path.realpath(tmp_path)

    def test_special_chars(self, tmp_path):
        """Test a directory and file with special characters."""
        dir_name = "gamedir 2! (The Redirening)"
        file_name = "123 !@#$%^&()~S{}[]-=_+'`.bin"
        tmp_path = tmp_path / dir_name
        tmp_path.mkdir()
        (tmp_path / file_name).touch()
        files = gdipak.get_files_in_dir(tmp_path)
        assert len(files) == 1
        out_file_dir, out_file_name = path.split(files[0])
        assert out_file_name == file_name
        assert out_file_dir == path.realpath(tmp_path)

    def test_unrelated_file(self, tmp_path):
        """Test a directory containing unrelated files."""
        dir_name = "gamedirrrr"
        file_name = "Vacation Photo-1528.jpg"
        tmp_path = tmp_path / dir_name
        tmp_path.mkdir()
        (tmp_path / file_name).touch()
        files = gdipak.get_files_in_dir(tmp_path)
        assert len(files) == 0

    def test_multi_files(self, tmp_path):
        """Test a directory containing multiple files."""
        dir_name = "gamedir"
        file_names = (
            "mygame.gdi",
            "mygame(track1).bin",
            "mygame(track2).bin",
            "mygame(track3).raw",
            "mygame.txt",
        )
        tmp_path = tmp_path / dir_name
        tmp_path.mkdir()
        for file_name in file_names:
            (tmp_path / file_name).touch()
        files = gdipak.get_files_in_dir(tmp_path)
        assert len(files) == (len(file_names) - 1)
        for file in files:
            assert file != file_names[len(file_names) - 1]


class TestGetSubdirsInDir:
    """Test getting the sub directories in a directory."""

    def test_no_dirs(self, tmp_path):
        """Test when there are no directories."""
        tmp_path = tmp_path / "basedir"
        tmp_path.mkdir()
        dirs = gdipak.get_subdirs_in_dir(tmp_path)
        assert len(dirs) == 0

    def test_dirs(self, tmp_path):
        """Test when there are directories."""
        sub1 = tmp_path / "basedir" / "subdir0"
        sub1.mkdir(parents=True)
        sub2 = tmp_path / "basedir" / "subdir1"
        sub2.mkdir(parents=True)
        dirs = gdipak.get_subdirs_in_dir(tmp_path / "basedir")
        assert len(dirs) == 2
        assert str(sub1) in dirs
        assert str(sub2) in dirs

    def test_sub_dirs_recursive(self, tmp_path):
        """Test when there are sub directories."""

        def create_dirs_in_dir(base_dir, start_index):
            for i in range(2):
                sub_dir = base_dir / f"subdir{start_index + i}"
                sub_dir.mkdir()
                sub_dirs.append(str(sub_dir))

        base = tmp_path / "basedir"
        base.mkdir()
        sub_dirs = []
        create_dirs_in_dir(base, 0)
        create_dirs_in_dir(Path(sub_dirs[0]), 2)
        create_dirs_in_dir(Path(sub_dirs[2]), 4)
        dirs = gdipak.get_subdirs_in_dir(str(base))
        assert len(dirs) == 6
        assert sorted(dirs) == sorted(sub_dirs)

    def test_sub_dirs_recursive_with_max_recurion(self, tmp_path):
        """Test when there are sub directories and a recursion limit."""

        def create_dirs_in_dir(base_dir, start_index):
            for i in range(2):
                sub_dir = base_dir / f"subdir{start_index + i}"
                sub_dir.mkdir()
                sub_dirs.append(str(sub_dir))

        base = tmp_path / "basedir"
        base.mkdir()
        sub_dirs = []
        create_dirs_in_dir(base, 0)
        create_dirs_in_dir(Path(sub_dirs[0]), 2)
        create_dirs_in_dir(Path(sub_dirs[2]), 4)
        dirs = gdipak.get_subdirs_in_dir(str(base), 1)
        assert len(dirs) == 4
        assert sorted(dirs) == sorted(sub_dirs[:4])


class TestWriteFile:
    """Test getting the sub directories in a directory."""

    def test_same_file(self, tmpdir):
        """Tests reading and writing from the same directory."""
        io_dir = tmpdir.mkdir("Game!")
        in_file = io_dir.join("Game!.gdi")
        contents = b"This is the contents of the file"
        in_file.write(contents)

        out_file_path = path.join(io_dir, "disc.gdi")
        gdipak.write_file(in_file.realpath(), out_file_path)
        # original file still exists
        assert in_file.check()
        with open(out_file_path, "br") as out_file:
            assert contents == out_file.read()

    def test_different_file(self, tmpdir):
        """Tests reading and writing to different directories."""
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")

        out_dir = tmpdir.mkdir("outputdir")
        out_file_name = path.join(out_dir, "disc.gdi")
        gdipak.write_file(in_file.realpath(), out_file_name)

        # original file still exists
        assert in_file.check()
        with open(in_file, "br") as f_in:
            with open(out_file_name, "br") as f_out:
                assert f_in.read() == f_out.read()

    def test_missing_directory(self, tmpdir):
        """ "Test writing to a directory that doesn't exist."""
        in_dir = tmpdir.mkdir("Game!")
        in_file = in_dir.join("Game!.gdi")
        in_file.write(b"This is the contents of the file")

        out_dir = path.join(tmpdir, "outputdir")
        out_file_name = path.join(out_dir, "disc.gdi")
        gdipak.write_file(in_file.realpath(), out_file_name)

        # original file still exists
        assert in_file.check()
        with open(in_file, "br") as f_in:
            with open(out_file_name, "br") as f_out:
                assert f_in.read() == f_out.read()


class TestWriteNameFile:
    """Test writing the name file to the out directory."""

    def test_out_dir_exists_bare_gdi_file_str(self, tmpdir):
        """Test having a GDI file's name as input."""
        game_name = "Bill's Okay But Lonely Adventure- The Game"
        out_dir = tmpdir.mkdir(game_name)
        gdi_file_name = game_name + ".gdi"
        gdipak.write_name_file(out_dir, gdi_file_name)
        assert path.isfile(path.join(out_dir, game_name + ".txt"))

    def test_out_dir_exists_gdi_file_path(self, tmpdir):
        """Test having a GDI file's path as input."""
        game_name = "Morgan the Bull And Stanley the Bear Go To Market"
        out_dir = tmpdir.mkdir(game_name)
        gdi_file_path = path.join(out_dir, game_name + ".gdi")
        gdipak.write_name_file(out_dir, gdi_file_path)
        assert path.isfile(path.join(out_dir, game_name + ".txt"))

    def test_out_dir_doesnt_exist_bare_gdi_file_str(self, tmpdir):
        """Test output directory not existing and having a GDI file name as input."""
        game_name = "Somebody Once Told Me - Allstars!"
        out_dir = path.join(tmpdir, game_name)
        gdi_file_name = game_name + ".gdi"
        gdipak.write_name_file(out_dir, gdi_file_name)
        assert path.isfile(path.join(out_dir, game_name + ".txt"))


class TestPackGdi:
    """Test building the GDI format files."""

    def test_single_dir_same_out_dir(self, tmpdir):
        """Test in a single directory, dont create the namefile."""
        dir_path, in_file_names, exts = make_files(tmpdir, "mygame")
        gdipak.pack_gdi(dir_path, dir_path, False, False)

        # dir name didn't change
        assert tmpdir.listdir()[0] == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_same_out_dir_gen_namefile(self, tmpdir):
        """Test in a single directory, create the namefile."""
        dir_path, in_file_names, exts = make_files(tmpdir, "mygame")
        gdipak.pack_gdi(dir_path, dir_path, False, True)

        # dir name didn't change
        assert tmpdir.listdir()[0] == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_same_out_dir_default_args(self, tmpdir):
        """Test in a single directory with default arguments."""
        dir_path, in_file_names, exts = make_files(tmpdir, "mygame")
        gdipak.pack_gdi(dir_path, dir_path)

        # dir name didn't change
        assert tmpdir.listdir()[0] == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_different_out_dir(self, tmpdir):
        """Test creating the output in a separate directory."""
        in_dir, in_file_names, exts = make_files(tmpdir, "mygame")
        out_dir = tmpdir.mkdir("processed_game")
        gdipak.pack_gdi(in_dir, out_dir)

        # src files didn't change
        with scandir(in_dir) as itr:
            for item in itr:
                assert path.basename(item) in in_file_names
        dir_path = path.join(out_dir, path.basename(in_dir))
        check_files(dir_path, exts)

    def test_recursive_dir_bad_recursive_mode(self, tmpdir):
        """Test passing an invalid recursive mode."""
        dir_path, _1, _2 = make_files(tmpdir, "mygame")
        make_files(dir_path, "some other game")
        out_dir = tmpdir.mkdir("output")
        with pytest.raises(ValueError):
            gdipak.pack_gdi(dir_path, out_dir, "strawberry", False)

    def test_recursive_dir_same_out_dir_mode_none(self, tmpdir):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmpdir, "mygame")
        _0, sog_in_fielnames, _2 = make_files(dir_path, "some other game")
        gdipak.pack_gdi(dir_path, dir_path, None, False)
        check_files(dir_path, exts, mg_in_file_names)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    # subdir was not touched
                    with pytest.raises(AssertionError):
                        check_files(item, exts, sog_in_fielnames)

    def test_recursive_dir_same_out_dir_mode_zero(self, tmpdir):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmpdir, "mygame")
        _0, sog_in_fielnames, _2 = make_files(dir_path, "some other game")
        gdipak.pack_gdi(dir_path, dir_path, RecursiveMode.PRESERVE_STRUCTURE, False)
        check_files(dir_path, exts, mg_in_file_names)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    check_files(item, exts, sog_in_fielnames)

    def test_recursive_dir_same_out_dir_mode_one(self, tmpdir):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmpdir, "mygame")
        _0, sog_in_fielnames, _2 = make_files(dir_path, "some other game")
        # mode is changed implicitly due to in_dir == out_dir
        gdipak.pack_gdi(dir_path, dir_path, RecursiveMode.FLATTEN_STRUCTURE, False)
        check_files(dir_path, exts, mg_in_file_names)
        with scandir(dir_path) as itr:
            for item in itr:
                if path.isdir(item):
                    check_files(item, exts, sog_in_fielnames)

    def test_recursive_dir_different_out_dir_mode_one(self, tmpdir):
        """Test multiple sets of files in a recursive directory structure and a
        flat output directory."""
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        gdipak.pack_gdi(sg_dir, out_dir, RecursiveMode.FLATTEN_STRUCTURE)

        dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(dir_path, sg_exts)
        dir_path = path.join(out_dir, path.basename(sog_dir))
        check_files(dir_path, sog_exts)
        dir_path = path.join(out_dir, path.basename(soog_dir))
        check_files(dir_path, soog_exts)
        dir_path = path.join(out_dir, path.basename(sooog_dir))
        check_files(dir_path, sooog_exts)

    # pylint: disable=too-many-locals
    def test_recursive_dir_different_out_dir_mode_zero(self, tmpdir):
        """Test multiple sets of files in a recursive directory structure and an
        output directory structure the mirrors the input structure."""
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        gdipak.pack_gdi(sg_dir, out_dir, RecursiveMode.PRESERVE_STRUCTURE)

        sg_dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(sg_dir_path, sg_exts)
        sog_dir_path = path.join(sg_dir_path, path.basename(sog_dir))
        check_files(sog_dir_path, sog_exts)
        soog_dir_path = path.join(sg_dir_path, path.basename(soog_dir))
        check_files(soog_dir_path, soog_exts)
        sooog_dir_path = path.join(soog_dir_path, path.basename(sooog_dir))
        check_files(sooog_dir_path, sooog_exts)

    def test_missing_gdi_file(self, tmp_path):
        """Tests a set of files that does not include the gdi file."""
        name = "mygame"
        dir_path, _1, _2 = make_files(tmp_path, name)
        gdi_path = Path(path.join(dir_path, name + ".gdi"))
        gdi_path.unlink()
        with pytest.raises(ValueError):
            gdipak.pack_gdi(dir_path, dir_path)

    def test_too_many_gdi_files(self, tmp_path):
        """Tests a set of files with more than one gdi file."""
        name = "mygame"
        dir_path, _1, _2 = make_files(tmp_path, name)
        impostor_file = dir_path / "who put this file here.gdi"
        impostor_file.touch()
        with pytest.raises(ValueError):
            gdipak.pack_gdi(dir_path, dir_path)
