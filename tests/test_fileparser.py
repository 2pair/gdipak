import pytest
from gdipak.fileparser import FileParser
from os import path


class TestConvertFilename:
    def test_convert_gdi(self):
        result = FileParser.convert_filename("Very Good Game ~PAL~.gdi")
        assert result == "disc.gdi"

    def test_convert_file_names(self):
        result = FileParser.convert_filename("Very Good Game (Track 1) PAL.raw")
        assert result == "track01.raw"

        result = FileParser.convert_filename(
            "track racing game 2-track5-(region and language information).bin"
        )
        assert result == "track05.bin"

        result = FileParser.convert_filename(
            "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin"
        )
        assert result == "track08.bin"

        result = FileParser.convert_filename("_THE_GAME_TRACK_4_.bin")
        assert result == "track04.bin"

        result = FileParser.convert_filename("Sometimes.People.Do.This.Track.12.raw")
        assert result == "track12.raw"

    def test_convert_file_names_with_dirs(self, tmpdir):
        result = FileParser.convert_filename(
            path.join(tmpdir, "Very Good Game (Track 1) PAL.raw")
        )
        assert result == path.join(tmpdir, "track01.raw")

        result = FileParser.convert_filename(
            path.join(
                tmpdir,
                "track racing game 2-track5-(region and language information).bin",
            )
        )
        assert result == path.join(tmpdir, "track05.bin")

        result = FileParser.convert_filename(
            path.join(
                tmpdir,
                "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin",
            )
        )
        assert result == path.join(tmpdir, "track08.bin")

        result = FileParser.convert_filename(
            path.join(tmpdir, "_THE_GAME_TRACK_4_.bin")
        )
        assert result == path.join(tmpdir, "track04.bin")

        result = FileParser.convert_filename(
            path.join(tmpdir, "Sometimes.People.Do.This.Track.12.raw")
        )
        assert result == path.join(tmpdir, "track12.raw")

    def test_bad_file_type(self):
        with pytest.raises(ValueError):
            FileParser.convert_filename("Very Good Game.cdi")

    def test_ambiguous_file_name(self):
        with pytest.raises(SyntaxError):
            FileParser.convert_filename("Very Good Game.bin")


class TestGetOutputFileContents:
    def test_bin(self, tmpdir):
        file_name = path.join(tmpdir, "Gamma Gamea.bin")
        result = FileParser.get_output_file_contents(file_name)
        assert result == file_name

    def test_raw(self, tmpdir):
        file_name = path.join(tmpdir, "wwf.raw")
        result = FileParser.get_output_file_contents(file_name)
        assert result == file_name

    def test_gdi(self, tmpdir, monkeypatch):
        def mock_process_gdi(file_name):
            file_path, file_name = path.split(file_name)
            return path.join(file_path, "out_" + file_name)

        monkeypatch.setattr(FileParser, "process_gdi", mock_process_gdi)
        file_name = path.join(tmpdir, "Good Game Almighty.gdi")
        result = FileParser.get_output_file_contents(file_name)
        file_path, file_name = path.split(file_name)
        assert result == path.join(file_path, "out_" + file_name)

    def test_something_else(self, tmpdir):
        file_name = path.join(tmpdir, "War and Peace.rtf")
        with pytest.raises(ValueError):
            FileParser.get_output_file_contents(file_name)


# TODO
@pytest.mark.skip(reason="Havent written tests yet")
class TestProcessGdi:
    def test_a_test(self):
        assert False
