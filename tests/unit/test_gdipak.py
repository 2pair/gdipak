""" Tests for gdipak"""

from pathlib import Path
import pytest

from tests.testing_utils import make_files, check_files
from gdipak import gdipak
from gdipak.arg_parser import RecursiveMode


class TestPackGdi:
    """Test building the GDI format files."""

    def test_single_dir_same_out_dir(self, tmp_path):
        """Test in a single directory, dont create the namefile."""
        game_name = "mygame"
        dir_path, in_file_names, exts = make_files(tmp_path, game_name)
        game_dir = tmp_path / game_name
        gdipak.pack_gdi(dir_path, dir_path, False, False)

        # dir name didn't change
        assert game_dir == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_same_out_dir_gen_namefile(self, tmp_path):
        """Test in a single directory, create the namefile."""
        game_name = "mygame"
        dir_path, in_file_names, exts = make_files(tmp_path, game_name)
        gdipak.pack_gdi(dir_path, dir_path, False, True)
        game_dir = tmp_path / game_name

        # dir name didn't change
        assert game_dir == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_same_out_dir_default_args(self, tmp_path):
        """Test in a single directory with default arguments."""
        game_name = "mygame"
        dir_path, in_file_names, exts = make_files(tmp_path, game_name)
        gdipak.pack_gdi(dir_path, dir_path)
        game_dir = tmp_path / game_name

        # dir name didn't change
        assert game_dir == dir_path
        check_files(dir_path, exts, in_file_names)

    def test_single_dir_different_out_dir(self, tmp_path):
        """Test creating the output in a separate directory."""
        in_dir, in_file_names, exts = make_files(tmp_path, "mygame")
        out_dir = tmp_path / "processed_game"
        out_dir.mkdir()
        gdipak.pack_gdi(in_dir, out_dir)

        # src files didn't change
        for item in in_dir.iterdir():
            assert item.name in in_file_names
        dir_path = out_dir / in_dir.name
        check_files(dir_path, exts)

    def test_recursive_dir_bad_recursive_mode(self, tmp_path):
        """Test passing an invalid recursive mode."""
        dir_path, _1, _2 = make_files(tmp_path, "mygame")
        make_files(dir_path, "some other game")
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        with pytest.raises(ValueError):
            gdipak.pack_gdi(dir_path, out_dir, "strawberry", False)

    def test_recursive_dir_same_out_dir_mode_none(self, tmp_path):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmp_path, "mygame")
        _0, sog_in_file_names, _2 = make_files(dir_path, "some other game")
        gdipak.pack_gdi(dir_path, dir_path, None, False)
        check_files(dir_path, exts, mg_in_file_names)
        for item in dir_path.iterdir():
            if item.is_dir():
                # subdir was not touched
                with pytest.raises(AssertionError):
                    check_files(item, exts, sog_in_file_names)

    def test_recursive_dir_same_out_dir_mode_zero(self, tmp_path):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmp_path, "mygame")
        _0, sog_in_file_names, _2 = make_files(dir_path, "some other game")
        gdipak.pack_gdi(dir_path, dir_path, RecursiveMode.PRESERVE_STRUCTURE, False)
        check_files(dir_path, exts, mg_in_file_names)
        for item in dir_path.iterdir():
            if item.is_dir():
                check_files(item, exts, sog_in_file_names)

    def test_recursive_dir_same_out_dir_mode_one(self, tmp_path):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmp_path, "mygame")
        _0, sog_in_file_names, _2 = make_files(dir_path, "some other game")
        # mode is changed implicitly due to in_dir == out_dir
        gdipak.pack_gdi(dir_path, dir_path, RecursiveMode.FLATTEN_STRUCTURE, False)
        check_files(dir_path, exts, mg_in_file_names)
        for item in dir_path.iterdir():
            if item.is_dir():
                check_files(item, exts, sog_in_file_names)

    def test_recursive_dir_different_out_dir_mode_one(self, tmp_path):
        """Test multiple sets of files in a recursive directory structure and a
        flat output directory."""
        sg_dir, _1, sg_exts = make_files(tmp_path, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmp_path / "processed_game"
        out_dir.mkdir()

        gdipak.pack_gdi(sg_dir, out_dir, RecursiveMode.FLATTEN_STRUCTURE)

        check_files((out_dir / sg_dir.name), sg_exts)
        check_files((out_dir / sog_dir.name), sog_exts)
        check_files((out_dir / soog_dir.name), soog_exts)
        check_files((out_dir / sooog_dir.name), sooog_exts)

    # pylint: disable=too-many-locals
    def test_recursive_dir_different_out_dir_mode_zero(self, tmp_path):
        """Test multiple sets of files in a recursive directory structure and an
        output directory structure the mirrors the input structure."""
        sg_dir, _1, sg_exts = make_files(tmp_path, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmp_path / "processed_game"
        out_dir.mkdir()
        gdipak.pack_gdi(sg_dir, out_dir, RecursiveMode.PRESERVE_STRUCTURE)

        sg_dir_path = out_dir / sg_dir.name
        check_files(sg_dir_path, sg_exts)
        sog_dir_path = sg_dir_path / sog_dir.name
        check_files(sog_dir_path, sog_exts)
        soog_dir_path = sg_dir_path / soog_dir.name
        check_files(soog_dir_path, soog_exts)
        sooog_dir_path = soog_dir_path / sooog_dir.name
        check_files(sooog_dir_path, sooog_exts)

    def test_missing_gdi_file(self, tmp_path):
        """Tests a set of files that does not include the gdi file."""
        name = "mygame"
        dir_path, _1, _2 = make_files(tmp_path, name)
        gdi_path = Path(dir_path) / (name + ".gdi")
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
