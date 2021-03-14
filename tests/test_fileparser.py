
import pytest
from fileparser import FileParser

class TestConvertFilename:
    def test_convert_gdi(self):
        result = FileParser.convert_filename("Very Good Game ~PAL~.gdi")
        assert(result == "disc.gdi")

    def test_convert_tracks(self):
        result = FileParser.convert_filename("Very Good Game (Track 1) PAL.raw")
        assert(result == "track01.raw")

        result = FileParser.convert_filename("track racing game 2-track5-(region and language information).bin")
        assert(result == "track05.bin")

        result = FileParser.convert_filename("It's Incredible! - Worldwide?! (Europe) (En,Fr,De,Es) (Track0008).bin")
        assert(result == "track08.bin")

        result = FileParser.convert_filename("_THE_GAME_TRACK_4_.bin")
        assert(result == "track04.bin")

        result = FileParser.convert_filename("Sometimes.People.Do.This.Track.12.raw")
        assert(result == "track12.raw")

    def test_bad_file_type(self):
        with pytest.raises(ValueError):
            FileParser.convert_filename("Very Good Game.cdi")

    def test_ambiguous_file_name(self):
        with pytest.raises(SyntaxError):
            FileParser.convert_filename("Very Good Game.bin")
