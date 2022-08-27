import string

from tests.utils import GdiGenerator


class TestGdiGenerator:
    """Tests the GDI generator, which is used to test other tests."""

    # pytest disable=too-many-locals
    def test_fully_specified_gdi(self):
        """Test creating a GDI file with all information provided."""
        name = "It's Only Tuesday (Jp)"
        offsets = [0, 1000, 20000, 300000]
        exts = ["bin", "bin", "bin", "raw"]
        game_number = 2345
        line_end = "\r\n"
        generator = GdiGenerator(name, offsets, exts, game_number, line_end)
        gdi, metadata = generator()
        assert metadata["name"] == name
        assert metadata["game_num"] == game_number
        assert metadata["offsets"] == offsets
        assert metadata["extensions"] == exts
        assert metadata["line_end"] == line_end
        gdi_lines = gdi.splitlines(True)
        # Extra line because first line has the track count
        assert len(gdi_lines) == (len(offsets) + 1)
        for index, line in enumerate(gdi_lines):
            assert line[-2:] == line_end
            if index == 0:
                assert int(line.strip()) == (len(gdi_lines) - 1)
                continue
            pre_title, title, zero = line.split('"', 2)
            assert title == f"{name} (Track {index}).{exts[index - 1]}"
            assert zero.strip() == "0"
            track_num, offset, four_oh, game_num = pre_title.split()
            assert int(track_num) == index
            assert int(offset) == offsets[index - 1]
            assert int(four_oh) == (4 * ((index) % 2))
            assert int(game_num) == game_number

    # pytest disable=too-many-locals
    def test_fully_random_gdi(self):
        """Test creating a GDI file with the minimum information provided."""
        name_a = "It's Wednesday Now (En/Fr/De/Es/It)"
        name_b = "Here Comes Thursday (USA) (v1.1b)"
        generator = GdiGenerator(name_a)
        gdi_a, _ = generator()
        line_end_a = gdi_a.split("\n")[0].lstrip(string.digits) + "\n"
        gdi_lines_a = gdi_a.splitlines()
        track_count_a = int(gdi_lines_a[0].strip())
        generator.game_name = name_b
        # Statistically unlikely that this fails
        for _ in range(20):
            gdi_b, _ = generator()
            line_end_b = gdi_b.split("\n")[0].lstrip(string.digits) + "\n"
            gdi_lines_b = gdi_b.splitlines()
            track_count_b = int(gdi_lines_b[0].strip())
            if track_count_b == 2:
                continue
            if line_end_a != line_end_b and track_count_a != track_count_b:
                break
        else:
            assert False

        line_a = gdi_lines_a[2]
        line_b = gdi_lines_b[2]
        pre_title_a, _title_a, _ = line_a.split('"', 2)
        pre_title_b, _title_b, _ = line_b.split('"', 2)
        track_num_a, offset_a, four_oh_a, game_num_a = pre_title_a.split()
        track_num_b, offset_b, four_oh_b, game_num_b = pre_title_b.split()
        assert int(track_num_a) == int(track_num_b)
        assert int(offset_a) != int(offset_b)
        assert int(four_oh_a) == int(four_oh_b)
        assert int(game_num_a) != int(game_num_b)
