"""Tests for the file processor class."""

from os import path
import pytest

from gdipak.file_processor import FileProcessor


class TestConvertFileName:
    """Tests file name conversion"""

    def test_convert_gdi(self):
        """Tests converting a gdi file name."""
        result = FileProcessor.convert_file_name("Very Good Game ~PAL~.gdi")
        assert result == "disc.gdi"

    def test_convert_track_names(self):
        """Tests converting track names."""
        result = FileProcessor.convert_file_name("Very Good Game (Track 1) PAL.raw")
        assert result == "track01.raw"

        result = FileProcessor.convert_file_name(
            "track racing game 2-track5-(region and language information).bin"
        )
        assert result == "track05.bin"

        result = FileProcessor.convert_file_name(
            "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin"
        )
        assert result == "track08.bin"

        result = FileProcessor.convert_file_name("_THE_GAME_TRACK_4_.bin")
        assert result == "track04.bin"

        result = FileProcessor.convert_file_name(
            "Sometimes.People.Do.This.Track.12.raw"
        )
        assert result == "track12.raw"

    def test_convert_track_names_with_dirs(self, tmpdir):
        """Tests converting paths to tracks."""
        result = FileProcessor.convert_file_name(
            path.join(tmpdir, "Very Good Game (Track 1) PAL.raw")
        )
        assert result == path.join(tmpdir, "track01.raw")

        result = FileProcessor.convert_file_name(
            path.join(
                tmpdir,
                "track racing game 2-track5-(region and language information).bin",
            )
        )
        assert result == path.join(tmpdir, "track05.bin")

        result = FileProcessor.convert_file_name(
            path.join(
                tmpdir,
                "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin",
            )
        )
        assert result == path.join(tmpdir, "track08.bin")

        result = FileProcessor.convert_file_name(
            path.join(tmpdir, "_THE_GAME_TRACK_4_.bin")
        )
        assert result == path.join(tmpdir, "track04.bin")

        result = FileProcessor.convert_file_name(
            path.join(tmpdir, "Sometimes.People.Do.This.Track.12.raw")
        )
        assert result == path.join(tmpdir, "track12.raw")

    def test_bad_file_type(self):
        """Tests fails when given an invalid file type."""
        with pytest.raises(ValueError):
            FileProcessor.convert_file_name("Very Good Game.cdi")

    def test_ambiguous_file_name(self):
        """Test fails when given a track of unknown number."""
        with pytest.raises(SyntaxError):
            FileProcessor.convert_file_name("Very Good Game.bin")

        with pytest.raises(SyntaxError):
            FileProcessor.convert_file_name("Track_Attack.bin")


class TestGetOutputFileContents:
    """Tests the mapping from input file name to output file contents location."""

    def test_bin(self, tmpdir):
        """Test bin file."""
        file_name = path.join(tmpdir, "Gamma Gamea.bin")
        result = FileProcessor.get_output_file_contents(file_name)
        assert result == file_name

    def test_raw(self, tmpdir):
        """Test raw file."""
        file_name = path.join(tmpdir, "wwf.raw")
        result = FileProcessor.get_output_file_contents(file_name)
        assert result == file_name

    def test_gdi(self, tmpdir, monkeypatch):
        """Test gdi file."""

        def mock_process_gdi(file_name):
            file_path, file_name = path.split(file_name)
            return path.join(file_path, "out_" + file_name)

        monkeypatch.setattr(FileProcessor, "process_gdi", mock_process_gdi)
        file_name = path.join(tmpdir, "Good Game Almighty.gdi")
        result = FileProcessor.get_output_file_contents(file_name)
        file_path, file_name = path.split(file_name)
        assert result == path.join(file_path, "out_" + file_name)

    def test_unsupported(self, tmpdir):
        """Test an unsupported file format."""
        file_name = path.join(tmpdir, "War and Peace.rtf")
        with pytest.raises(ValueError):
            FileProcessor.get_output_file_contents(file_name)
