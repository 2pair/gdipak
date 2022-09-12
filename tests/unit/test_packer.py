"""Tests for game packer"""

import pytest

from gdipak.packer import BasePacker, MovePacker, CopyPacker
from tests.testing_utils import make_files


@pytest.fixture(scope="function", autouse=True)
def mock_convert_file_name(monkeypatch):
    """Patch convert file name function."""
    monkeypatch.setattr(
        "gdipak.file_utils.convert_file_name",
        lambda in_file: in_file.name,
    )


@pytest.fixture(scope="function", autouse=True)
def mock_convert_file(monkeypatch):
    """Patch convert file function."""
    monkeypatch.setattr(
        "gdipak.gdi_converter.GdiConverter.convert_file", lambda _self: None
    )


class TestPacker:
    """Tests for the base packer class."""

    def test_instantiate_base_packer(self):
        """Tests importing abstract base class"""
        with pytest.raises(TypeError) as ex:
            BasePacker(".", ".")  # pylint: disable=abstract-class-instantiated
        assert "Can't instantiate abstract class BasePacker" in str(ex.value)

    def test_missing_gdi_file(self, tmp_path):
        """Tests a directory that does not contain a GDI file."""
        game_dir, _, _ = make_files(tmp_path, "Bo Diddley's Conquest")
        gdi_file = next(file for file in game_dir.iterdir() if file.suffix == ".gdi")
        gdi_file.unlink()
        with pytest.raises(ValueError) as ex:
            MovePacker(game_dir, game_dir)
        assert "Directory does not contain a gdi file" in str(ex.value)

    def test_too_many_gdi_files(self, tmp_path):
        """Tests a directory that contains more than one GDI file."""
        game_dir, _, _ = make_files(tmp_path, "Rasputin on the Ritz")
        gdi_file = next(file for file in game_dir.iterdir() if file.suffix == ".gdi")
        gdi_file = gdi_file.parent / ("The Sullen Sultan" + gdi_file.suffix)
        gdi_file.touch()
        with pytest.raises(ValueError) as ex:
            MovePacker(game_dir, game_dir)
        assert "Directory contains more than one gdi file" in str(ex.value)

    def test_create_name_file(self, tmp_path):
        """Tests That the name file gets created"""

        class LocalPacker(BasePacker):
            """It isn't abstract"""

            def file_action(self, _in_file, _out_file):
                pass

        game_name = "Action at a Distance"
        game_dir, _, _ = make_files(tmp_path, game_name)
        packer = LocalPacker(game_dir, game_dir)
        packer.package_game(create_name_file=True)
        assert (game_dir / game_name).exists()


class TestCopyPacker:
    """Tests for the copy packer class."""

    def test_same_directory(self, tmp_path):
        """Tests copying files from one directory to itself."""
        game_dir, _, _ = make_files(tmp_path, "Melting in the Moonlight")
        in_files = [file.name for file in game_dir.iterdir()]
        packer = CopyPacker(game_dir, game_dir)
        packer.package_game()
        out_files = [file.name for file in game_dir.iterdir()]
        assert len(in_files) == len(out_files)
        for out_file in out_files:
            assert out_file in in_files
        for in_file in in_files:
            assert in_file in out_files

    def test_different_directories(self, tmp_path):
        """Tests copying files from one directory to another."""
        game_dir, _, _ = make_files(tmp_path, "Melting in the Moonlight")
        in_files = [file.name for file in game_dir.iterdir()]
        out_dir = tmp_path / "out_dir"
        out_dir.mkdir()
        packer = CopyPacker(game_dir, out_dir)
        packer.package_game()
        out_files = [file.name for file in game_dir.iterdir()]
        assert len(in_files) == len(out_files)
        for out_file in out_files:
            assert out_file in in_files
        for in_file in in_files:
            assert in_file in out_files


class TestMovePacker:
    """Tests for the copy packer class."""

    def test_same_directory(self, tmp_path):
        """Tests moving files from one directory to itself."""
        game_dir, _, _ = make_files(tmp_path, "Melting in the Moonlight")
        in_files = [file.name for file in game_dir.iterdir()]
        packer = MovePacker(game_dir, game_dir)
        packer.package_game()
        out_files = [file.name for file in game_dir.iterdir()]
        assert len(in_files) == len(out_files)
        for out_file in out_files:
            assert out_file in in_files
        for in_file in in_files:
            assert in_file in out_files

    def test_different_directories(self, tmp_path):
        """Tests moving files from one directory to another."""
        game_dir, _, _ = make_files(tmp_path, "Melting in the Moonlight")
        in_files = [file.name for file in game_dir.iterdir()]
        out_dir = tmp_path / "out_dir"
        out_dir.mkdir()
        packer = MovePacker(game_dir, out_dir)
        packer.package_game()
        out_files = [file.name for file in out_dir.iterdir()]
        assert len(in_files) == len(out_files)
        assert len(list(game_dir.iterdir())) == 0
        for out_file in out_files:
            assert out_file in in_files
        for in_file in in_files:
            assert in_file in out_files
