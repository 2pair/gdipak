"""Tests for the file processor class."""

from pathlib import Path
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
            Path(tmpdir) / "Very Good Game (Track 1) PAL.raw"
        )
        assert result == "track01.raw"

        result = FileProcessor.convert_file_name(
            Path(tmpdir)
            / "track racing game 2-track5-(region and language information).bin"
        )
        assert result == "track05.bin"

        result = FileProcessor.convert_file_name(
            Path(tmpdir)
            / "It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin"
        )
        assert result == "track08.bin"

        result = FileProcessor.convert_file_name(
            Path(tmpdir) / "_THE_GAME_TRACK_4_.bin"
        )
        assert result == "track04.bin"

        result = FileProcessor.convert_file_name(
            Path(tmpdir) / "Sometimes.People.Do.This.Track.12.raw"
        )
        assert result == "track12.raw"

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
