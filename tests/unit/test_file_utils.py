"""Tests for utils.py"""

from collections import namedtuple
from pathlib import Path
import pytest

from gdipak.arg_parser import RecursiveMode
from gdipak import file_utils

from tests.testing_utils import create_dirs_in_dir


class TestWriteFile:
    """Test getting the sub directories in a directory."""

    def test_same_file(self, tmp_path):
        """Tests Passing the same file as input and output."""
        io_dir = tmp_path / "Game!"
        io_dir.mkdir()
        in_file_path = io_dir / "Game!.gdi"
        contents = b"This is the contents of the file"
        in_file_path.write_bytes(contents)

        out_file_path = in_file_path
        file_utils.write_file(in_file_path, out_file_path)
        # No errors occurred.
        assert in_file_path.exists()
        assert in_file_path.samefile(out_file_path)

    def test_same_file_with_path_arguments(self, tmp_path):
        """Tests Passing the same file as input and output."""
        io_dir = tmp_path / "Game!"
        io_dir.mkdir()
        in_file_path = io_dir / "Game!.gdi"
        contents = b"This is the contents of the file"
        in_file_path.write_bytes(contents)

        out_file_path = in_file_path
        file_utils.write_file(Path(in_file_path), Path(out_file_path))
        # No errors occurred.
        assert in_file_path.exists()
        assert in_file_path.samefile(out_file_path)

    def test_same_directory(self, tmp_path):
        """Tests reading and writing from the same directory."""
        io_dir = tmp_path / "Game!"
        io_dir.mkdir()
        in_file_path = io_dir / "Game!.gdi"
        contents = b"This is the contents of the file"
        in_file_path.write_bytes(contents)

        out_file_path = io_dir / "disc.gdi"
        file_utils.write_file(in_file_path, out_file_path)
        # original file still exists
        assert in_file_path.exists()
        assert out_file_path.read_bytes() == contents

    def test_different_directories(self, tmp_path):
        """Tests reading and writing to different directories."""
        in_dir = tmp_path / "Game!"
        in_dir.mkdir()
        in_file_path = in_dir / "Game!.gdi"
        in_file_path.write_bytes(b"This is the contents of the file")

        out_dir = tmp_path / "outputdir"
        out_dir.mkdir()
        out_file_path = out_dir / "disc.gdi"
        file_utils.write_file(str(in_file_path), str(out_file_path))
        # original file still exists
        assert in_file_path.exists()
        assert in_file_path.read_bytes() == out_file_path.read_bytes()

    def test_missing_directory(self, tmp_path):
        """ "Test writing to a directory that doesn't exist."""
        in_dir = tmp_path / "Game!"
        in_dir.mkdir()
        in_file_path = in_dir / "Game!.gdi"
        in_file_path.write_bytes(b"This is the contents of the file")

        out_file_path = tmp_path / "outputdir" / "disc.gdi"
        file_utils.write_file(in_file_path, out_file_path)
        # original file still exists
        assert in_file_path.exists()
        assert in_file_path.read_bytes() == out_file_path.read_bytes()


class TestGetSubdirsInDir:
    """Test getting the sub directories in a directory."""

    def test_no_dirs(self, tmp_path):
        """Test when there are no directories."""
        tmp_path = tmp_path / "basedir"
        tmp_path.mkdir()
        dirs = file_utils.get_sub_dirs_in_dir(tmp_path)
        assert len(dirs) == 0

    def test_dirs(self, tmp_path):
        """Test when there are directories."""
        sub1 = tmp_path / "basedir" / "subdir0"
        sub1.mkdir(parents=True)
        sub2 = tmp_path / "basedir" / "subdir1"
        sub2.mkdir(parents=True)
        dirs = file_utils.get_sub_dirs_in_dir(tmp_path / "basedir")
        assert len(dirs) == 2
        assert sub1 in dirs
        assert sub2 in dirs

    def test_dirs_with_string_argument(self, tmp_path):
        """Test when there are directories."""
        sub1 = tmp_path / "basedir" / "subdir0"
        sub1.mkdir(parents=True)
        sub2 = tmp_path / "basedir" / "subdir1"
        sub2.mkdir(parents=True)
        dirs = file_utils.get_sub_dirs_in_dir(str(tmp_path / "basedir"))
        assert len(dirs) == 2
        assert sub1 in dirs
        assert sub2 in dirs

    def test_sub_dirs_recursive(self, tmp_path):
        """Test when there are sub directories."""
        base = tmp_path / "basedir"
        base.mkdir()
        sub_dirs = create_dirs_in_dir(base, count=2)
        sub_dirs.extend(create_dirs_in_dir(Path(sub_dirs[0]), count=2, start_index=2))
        sub_dirs.extend(create_dirs_in_dir(Path(sub_dirs[2]), count=2, start_index=4))
        out_dirs = file_utils.get_sub_dirs_in_dir(str(base))
        assert len(out_dirs) == 6
        for out_dir, sub_dir in zip(sorted(out_dirs), sorted(sub_dirs)):
            assert out_dir.samefile(sub_dir)

    def test_sub_dirs_recursive_with_max_recursion(self, tmp_path):
        """Test when there are sub directories and a recursion limit."""
        base = tmp_path / "basedir"
        base.mkdir()
        sub_dirs = create_dirs_in_dir(base, count=2)
        sub_dirs.extend(create_dirs_in_dir(Path(sub_dirs[0]), count=2, start_index=2))
        sub_dirs.extend(create_dirs_in_dir(Path(sub_dirs[2]), count=2, start_index=4))
        dirs = file_utils.get_sub_dirs_in_dir(str(base), 1)
        assert len(dirs) == 4
        for out_dir, sub_dir in zip(sorted(dirs), sorted(sub_dirs[:4])):
            assert out_dir.samefile(sub_dir)


class TestGetGameFilesInDir:
    """Tests getting a list of all the files in the directory."""

    def test_alphanumeric(self, tmp_path):
        """Test a directory and file with only alphanumeric characters."""
        dir_name = "gamedir"
        file_name = "aBcD1234.gdi"
        game_path = tmp_path / dir_name
        game_path.mkdir()
        (game_path / file_name).touch()
        files = file_utils.get_game_files_in_dir(game_path)
        assert len(files) == 1
        file = files[0]
        assert file.name == file_name
        assert file.parent == game_path

    def test_with_path_argument(self, tmp_path):
        """Test passing a Path as the argument."""
        dir_name = "gamedir"
        file_name = "aBcD1234.gdi"
        game_path = tmp_path / dir_name
        game_path.mkdir()
        (game_path / file_name).touch()
        files = file_utils.get_game_files_in_dir(Path(game_path))
        assert len(files) == 1
        file = files[0]
        assert file.name == file_name
        assert file.parent == game_path

    def test_special_chars(self, tmp_path):
        """Test a directory and file with special characters."""
        dir_name = "gamedir 2! (The Re-direning)"
        file_name = r"123 !@#$%^&()~S\{\}[]-=_+'`.bin"
        game_path = tmp_path / dir_name
        game_path.mkdir()
        (game_path / file_name).touch()
        files = file_utils.get_game_files_in_dir(game_path)
        assert len(files) == 1
        file = files[0]
        assert file.name == file_name
        assert file.parent == game_path

    def test_unrelated_file(self, tmp_path):
        """Test a directory containing unrelated files."""
        dir_name = "gamedirrrr"
        file_name = "Vacation Photo-1528.jpg"
        game_path = tmp_path / dir_name
        game_path.mkdir()
        (game_path / file_name).touch()
        files = file_utils.get_game_files_in_dir(game_path)
        assert len(files) == 0

    def test_multi_files(self, tmp_path):
        """Test a directory containing multiple files."""
        dir_name = "gamedir"
        file_names = (
            "mygame.gdi",
            "mygame(track1).bin",
            "mygame(track2).bin",
            "mygame(track3).raw",
            "mygame",
        )
        game_path = tmp_path / dir_name
        game_path.mkdir()
        for file_name in file_names:
            (game_path / file_name).touch()
        files = file_utils.get_game_files_in_dir(game_path)
        assert len(files) == (len(file_names) - 1)
        for file in files:
            assert file != file_names[len(file_names) - 1]


class TestWriteNameFile:
    """Test writing the name file to the out directory."""

    def test_out_dir_exists_bare_gdi_file_str(self, tmp_path):
        """Test having a GDI file's name as input."""
        game_name = "Bill's Okay But Lonely Adventure- The Game"
        out_dir = tmp_path / game_name
        out_dir.mkdir()
        gdi_file_name = game_name + ".gdi"
        file_utils.write_name_file(out_dir, gdi_file_name)
        file_name = Path(out_dir) / game_name
        assert file_name.is_file()

    def test_out_dir_exists_bare_gdi_file_str_out_dir_as_str(self, tmp_path):
        """Test having a GDI file's name as input."""
        game_name = "Bill's Okay But Lonely Adventure- The Game"
        out_dir = tmp_path / game_name
        out_dir.mkdir()
        gdi_file_name = game_name + ".gdi"
        file_utils.write_name_file(str(out_dir), gdi_file_name)
        file_name = Path(out_dir) / game_name
        assert file_name.is_file()

    def test_out_dir_exists_gdi_file_path(self, tmp_path):
        """Test having a GDI file's path as input."""
        game_name = "Morgan the Bull And Stanley the Bear Go To Market"
        out_dir = tmp_path / game_name
        out_dir.mkdir()
        gdi_file_path = out_dir / (game_name + ".gdi")
        file_utils.write_name_file(out_dir, gdi_file_path)
        file_name = Path(out_dir) / game_name
        assert file_name.is_file()

    def test_out_dir_exists_gdi_file_path_as_path(self, tmp_path):
        """Test having a GDI file's path as input."""
        game_name = "Morgan the Bull And Stanley the Bear Go To Market"
        out_dir = tmp_path / game_name
        out_dir.mkdir()
        gdi_file_path = out_dir / (game_name + ".gdi")
        file_utils.write_name_file(out_dir, Path(gdi_file_path))
        file_name = Path(out_dir) / game_name
        assert file_name.is_file()

    def test_out_dir_does_not_exist_bare_gdi_file_str(self, tmp_path):
        """Test output directory not existing and having a GDI file name as input."""
        game_name = "Somebody Once Told Me - Allstars!"
        out_dir = tmp_path / game_name
        gdi_file_name = game_name + ".gdi"
        file_utils.write_name_file(out_dir, gdi_file_name)
        file_name = Path(out_dir) / game_name
        assert file_name.is_file()


class TestTransposePath:
    """Tests for the transpose_path function."""

    GamePaths = namedtuple("GamePaths", "in_dir local_game_dir game_dir out_dir")

    @pytest.fixture
    def game_paths(self, tmp_path):
        """Setup directories."""
        in_dir = tmp_path / "input"
        local_game_dir = Path("breakfast games") / "Egg Monger II"
        game_dir = in_dir / local_game_dir
        out_dir = tmp_path / "output"
        return self.GamePaths(in_dir, local_game_dir, game_dir, out_dir)

    def test_paths_and_preserve_mode(self, game_paths):
        """Test passing arguments as Paths."""
        game_out_dir = file_utils.transpose_path(
            game_path=game_paths.game_dir,
            in_base_path=game_paths.in_dir,
            out_base_path=game_paths.out_dir,
            mode=RecursiveMode.PRESERVE_STRUCTURE,
        )
        assert game_out_dir == game_paths.out_dir / game_paths.local_game_dir

    def test_strings_and_preserve_mode(self, game_paths):
        """Test passing arguments as strings."""
        game_out_dir = file_utils.transpose_path(
            game_path=str(game_paths.game_dir),
            in_base_path=str(game_paths.in_dir),
            out_base_path=str(game_paths.out_dir),
            mode=RecursiveMode.PRESERVE_STRUCTURE,
        )
        assert game_out_dir == game_paths.out_dir / game_paths.local_game_dir

    def test_flatten_mode(self, game_paths):
        """Test passing arguments as Paths."""
        game_out_dir = file_utils.transpose_path(
            game_path=game_paths.game_dir,
            in_base_path=game_paths.in_dir,
            out_base_path=game_paths.out_dir,
            mode=RecursiveMode.FLATTEN_STRUCTURE,
        )
        assert game_out_dir == game_paths.out_dir / game_paths.local_game_dir.name


class TestConvertFileName:
    """Tests file name conversion"""

    def test_convert_gdi(self):
        """Tests converting a gdi file name."""
        result = file_utils.convert_file_name("Very Good Game ~PAL~.gdi")
        assert result == "disc.gdi"

    def test_convert_track_names(self):
        """Tests converting track names."""
        result = file_utils.convert_file_name("Very Good Game (Track 1) PAL.raw")
        assert result == "track01.raw"

        result = file_utils.convert_file_name(
            "track racing game 2-track5-(region and language information).bin"
        )
        assert result == "track05.bin"

        result = file_utils.convert_file_name(
            "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin"
        )
        assert result == "track08.bin"

        result = file_utils.convert_file_name("_THE_GAME_TRACK_4_.bin")
        assert result == "track04.bin"

        result = file_utils.convert_file_name("Sometimes.People.Do.This.Track.12.raw")
        assert result == "track12.raw"

    def test_convert_track_names_with_dirs(self, tmpdir):
        """Tests converting paths to tracks."""
        result = file_utils.convert_file_name(
            Path(tmpdir) / "Very Good Game (Track 1) PAL.raw"
        )
        assert result == "track01.raw"

        result = file_utils.convert_file_name(
            Path(tmpdir)
            / "track racing game 2-track5-(region and language information).bin"
        )
        assert result == "track05.bin"

        result = file_utils.convert_file_name(
            Path(tmpdir)
            / "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin"
        )
        assert result == "track08.bin"

        result = file_utils.convert_file_name(Path(tmpdir) / "_THE_GAME_TRACK_4_.bin")
        assert result == "track04.bin"

        result = file_utils.convert_file_name(
            Path(tmpdir) / "Sometimes.People.Do.This.Track.12.raw"
        )
        assert result == "track12.raw"

    def test_bad_file_type(self):
        """Tests fails when given an invalid file type."""
        with pytest.raises(ValueError):
            file_utils.convert_file_name("Very Good Game.cdi")

    def test_ambiguous_file_name(self):
        """Test fails when given a track of unknown number."""
        with pytest.raises(SyntaxError):
            file_utils.convert_file_name("Very Good Game.bin")

        with pytest.raises(SyntaxError):
            file_utils.convert_file_name("Track_Attack.bin")
