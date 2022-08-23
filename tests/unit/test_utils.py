from tests.utils import GdiGenerator


class TestGdiGenerator:
    """Tests the GDI generator, which is used to test other tests."""

    # pytest disable:too-many-locals
    def test_fulled_specified_gdi(self):
        name = "It's Only Tuesday (Jp)"
        offsets = [0, 1000, 20000, 300000]
        exts = ["bin", "bin", "bin", "raw"]
        game_number = 2345
        line_end = "\r\n"
        generator = GdiGenerator(name, offsets, exts, game_number, line_end)
        gdi = generator()
        gdi_lines = gdi.splitlines(True)
        assert len(gdi_lines) == (len(offsets) + 1)
        for index, line in enumerate(gdi_lines):
            assert line[-2:] == line_end
            if index == 0:
                assert int(line.strip()) == (len(gdi_lines) - 1)
                continue
            pre_title, title, zero = line.split('"', 2)
            assert title == f"{name}.{exts[index - 1]}"
            assert zero.strip() == "0"
            track_num, offset, four_oh, game_num = pre_title.split()
            assert int(track_num) == index
            assert int(offset) == offsets[index - 1]
            assert int(four_oh) == (4 * ((index) % 2))
            assert int(game_num) == game_number
