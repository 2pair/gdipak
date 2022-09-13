"""Integration tests for gdipak"""

import pytest

from tests.testing_utils import make_files, check_files, check_games, GameData
import gdipak.__main__ as cli


class TestPackGdi:
    """Test building the GDI format files."""

    def test_single_dir_same_out_dir_modify(self, tmp_path):
        """Test in a single directory, dont create the namefile."""
        dir_path, _in_file_names, exts = make_files(tmp_path, "mygame")
        cli.main(["gdipak", "-i", str(dir_path), "-o", "in-dir", "-m", "modify"])
        check_files(dir_path, exts)

    def test_single_dir_same_out_dir_copy(self, tmp_path):
        """Test in a single directory, dont create the namefile."""
        dir_path, in_file_names, exts = make_files(tmp_path, "mygame")
        cli.main(["gdipak", "-i", str(dir_path), "-o", "in-dir", "-m", "copy"])
        expected_exts = exts + exts
        check_files(dir_path, expected_exts, in_file_names)

    def test_single_dir_same_out_dir_gen_namefile(self, tmp_path):
        """Test in a single directory, create the namefile."""
        dir_path, _in_file_names, exts = make_files(tmp_path, "mygame")
        cli.main(["gdipak", "-i", str(dir_path), "-o", "in-dir", "-m", "modify", "-n"])
        exts.append(None)
        check_files(dir_path, exts)

    def test_single_dir_different_out_dir(self, tmp_path):
        """Test creating the output in a separate directory."""
        in_dir, in_file_names, exts = make_files(tmp_path, "mygame")
        out_dir = tmp_path / "processed_game"
        out_dir.mkdir()
        cli.main(["gdipak", "-i", str(in_dir), "-o", str(out_dir), "-m", "modify"])

        # src files didn't change
        for item in in_dir.iterdir():
            assert item.name in in_file_names
        check_files(out_dir, exts)

    def test_recursive_dir_same_out_dir_copy(self, tmp_path):
        """Test multiple sets of files in a single directory."""
        dir_path, mg_in_file_names, exts = make_files(tmp_path, "mygame")
        _0, sog_in_file_names, _2 = make_files(dir_path, "some other game")
        cli.main(["gdipak", "-i", str(dir_path), "-o", str(dir_path), "-m", "copy"])

        check_files(dir_path, exts, mg_in_file_names)
        for item in dir_path.iterdir():
            if item.is_dir():
                # subdir was not touched
                with pytest.raises(AssertionError):
                    check_files(item, exts, sog_in_file_names)

    def test_recursive_dir_same_out_dir_mode_recursive_mode_zero(self, tmp_path):
        """Test multiple sets of files in a single directory."""
        game1_name = "mygame"
        game2_name = "some other game"
        _, game1_in_file_names, exts1 = make_files(tmp_path, game1_name)
        _, game2_in_file_names, exts2 = make_files(tmp_path, game2_name)
        cli.main(
            ["gdipak", "-i", str(tmp_path), "-o", str(tmp_path), "-m", "copy", "-r"]
        )
        games_data = []
        games_data.append(GameData(game1_name, exts1, game1_in_file_names))
        games_data.append(GameData(game2_name, exts2, game2_in_file_names))
        check_games(games_data, tmp_path)

    def test_recursive_dir_same_out_dir_mode_zero(self, tmp_path):
        """Test multiple sets of files in a single directory with additional nesting."""
        game1_name = "mygame"
        game2_name = "some other game"
        game3_name = "some other other game"
        _, game1_in_file_names, exts1 = make_files(tmp_path, game1_name)
        game2_path, game2_in_file_names, exts2 = make_files(tmp_path, game2_name)
        _, game3_in_file_names, exts3 = make_files(game2_path, game3_name)
        cli.main(
            [
                "gdipak",
                "-i",
                str(tmp_path),
                "-o",
                str(tmp_path),
                "-m",
                "copy",
                "-r",
                "0",
            ]
        )
        games_data = []
        games_data.append(GameData(game1_name, exts1, game1_in_file_names))
        games_data.append(GameData(game2_name, exts2, game2_in_file_names))
        check_games(games_data, tmp_path)
        games_data = [(GameData(game3_name, exts3, game3_in_file_names))]
        check_games(games_data, game2_path, fail_on_non_dirs=False)

    def test_recursive_dir_same_out_dir_mode_one(self, tmp_path):
        """Test multiple sets of files in a single directory with additional nesting."""
        game1_name = "mygame"
        game2_name = "some other game"
        game3_name = "some other other game"
        _, game1_in_file_names, exts1 = make_files(tmp_path, game1_name)
        game2_path, game2_in_file_names, exts2 = make_files(tmp_path, game2_name)
        _, game3_in_file_names, exts3 = make_files(game2_path, game3_name)
        cli.main(
            [
                "gdipak",
                "-i",
                str(tmp_path),
                "-o",
                str(tmp_path),
                "-m",
                "copy",
                "-r",
                "1",
            ]
        )
        games_data = []
        games_data.append(GameData(game1_name, exts1, game1_in_file_names))
        games_data.append(GameData(game2_name, exts2, game2_in_file_names))
        games_data.append(GameData(game3_name, exts3, game3_in_file_names))
        check_games(games_data, tmp_path)

    # pylint: disable=too-many-locals
    def test_recursive_dir_different_out_dir_mode_one(self, tmp_path):
        """Test multiple sets of files in a recursive directory structure and a
        flat output directory."""
        in_path = tmp_path / "input_games"
        in_path.mkdir()
        game1_name = "some game"
        game2_name = "some other game"
        game3_name = "some other other game"
        game4_name = "some other other other game"
        game1_path, game1_in_file_names, exts1 = make_files(in_path, game1_name)
        game2_path, game2_in_file_names, exts2 = make_files(game1_path, game2_name)
        game3_path, game3_in_file_names, exts3 = make_files(game2_path, game3_name)
        _, game4_in_file_names, exts4 = make_files(game3_path, game4_name)
        out_path = tmp_path / "processed_games"
        out_path.mkdir()

        cli.main(
            ["gdipak", "-i", str(in_path), "-o", str(out_path), "-m", "copy", "-r", "1"]
        )
        games_data = []
        games_data.append(GameData(game1_name, exts1, game1_in_file_names))
        games_data.append(GameData(game2_name, exts2, game2_in_file_names))
        games_data.append(GameData(game3_name, exts3, game3_in_file_names))
        games_data.append(GameData(game4_name, exts4, game4_in_file_names))
        check_games(games_data, out_path)

    # pylint: disable=too-many-locals
    def test_recursive_dir_different_out_dir_mode_zero(self, tmp_path):
        """Test multiple sets of files in a recursive directory structure and an
        output directory structure the mirrors the input structure."""
        in_path = tmp_path / "input_games"
        in_path.mkdir()
        game1_name = "some game"
        game2_name = "some other game"
        game3_name = "some other other game"
        game4_name = "some other other other game"
        game1_path, game1_in_file_names, exts1 = make_files(in_path, game1_name)
        game2_path, game2_in_file_names, exts2 = make_files(game1_path, game2_name)
        game3_path, game3_in_file_names, exts3 = make_files(game2_path, game3_name)
        _, game4_in_file_names, exts4 = make_files(game3_path, game4_name)
        out_path = tmp_path / "processed_games"
        out_path.mkdir()

        cli.main(
            ["gdipak", "-i", str(in_path), "-o", str(out_path), "-m", "copy", "-r", "0"]
        )
        games_data = [GameData(game1_name, exts1, game1_in_file_names)]
        check_games(games_data, out_path, fail_on_non_dirs=False)
        games_data = [GameData(game2_name, exts2, game2_in_file_names)]
        out_path = out_path / game1_name
        check_games(games_data, out_path, fail_on_non_dirs=False)
        games_data = [GameData(game3_name, exts3, game3_in_file_names)]
        out_path = out_path / game2_name
        check_games(games_data, out_path, fail_on_non_dirs=False)
        games_data = [GameData(game4_name, exts4, game4_in_file_names)]
        out_path = out_path / game3_name
        check_games(games_data, out_path, fail_on_non_dirs=False)

    def test_missing_gdi_file(self, tmp_path):
        """Tests a set of files that does not include the gdi file."""
        name = "mygame"
        path, _1, _2 = make_files(tmp_path, name)
        gdi_path = path / (name + ".gdi")
        gdi_path.unlink()
        with pytest.raises(ValueError) as ex:
            cli.main(["gdipak", "-i", str(path), "-o", str(path), "-m", "modify"])
        assert "Directory does not contain a gdi file" in str(ex.value)

    def test_too_many_gdi_files(self, tmp_path):
        """Tests a set of files with more than one gdi file."""
        name = "mygame"
        path, _1, _2 = make_files(tmp_path, name)
        impostor_file = path / "who put this file here.gdi"
        impostor_file.touch()
        with pytest.raises(ValueError) as ex:
            cli.main(["gdipak", "-i", str(path), "-o", str(path), "-m", "modify"])
        assert "Directory contains more than one gdi file" in str(ex.value)
