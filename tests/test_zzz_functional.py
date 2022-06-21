"""end to end functional tests"""

from os import path
from tests.utils import make_files, check_files

import gdipak.gdipak


class TestGdiPakFunctional:
    def test_recursive_dir_different_out_dir_mode_zero(self, tmpdir, monkeypatch):
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")

        monkeypatch.setattr(
            "gdipak.argv", ["pytest", "-d", str(sg_dir), "-o", str(out_dir), "-r", "0"]
        )
        gdipak.main()

        sg_dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(sg_dir_path, sg_exts)
        sog_dir_path = path.join(sg_dir_path, path.basename(sog_dir))
        check_files(sog_dir_path, sog_exts)
        soog_dir_path = path.join(sg_dir_path, path.basename(soog_dir))
        check_files(soog_dir_path, soog_exts)
        sooog_dir_path = path.join(soog_dir_path, path.basename(sooog_dir))
        check_files(sooog_dir_path, sooog_exts)

    def test_recursive_dir_different_out_dir_mode_one(self, tmpdir, monkeypatch):
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")

        monkeypatch.setattr(
            "gdipak.argv",
            ["pytest", "-d", str(sg_dir), "-o", str(out_dir), "-r", "1", "-n"],
        )
        gdipak.main()

        dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(dir_path, sg_exts)
        dir_path = path.join(out_dir, path.basename(sog_dir))
        check_files(dir_path, sog_exts)
        dir_path = path.join(out_dir, path.basename(soog_dir))
        check_files(dir_path, soog_exts)
        dir_path = path.join(out_dir, path.basename(sooog_dir))
        check_files(dir_path, sooog_exts)

    def test_recursive_dir_same_out_dir(self, tmpdir, monkeypatch):
        sg_dir, _1, sg_exts = make_files(tmpdir, "some game")
        sog_dir, _1, sog_exts = make_files(sg_dir, "some other game")
        soog_dir, _1, soog_exts = make_files(sg_dir, "some other other game")
        sooog_dir, _1, sooog_exts = make_files(soog_dir, "some other other other game")

        monkeypatch.setattr("gdipak.argv", ["pytest", "-d", str(sg_dir), "-m"])
        gdipak.main()

        sg_dir_path = path.join(tmpdir, path.basename(sg_dir))
        check_files(sg_dir_path, sg_exts)
        sog_dir_path = path.join(sg_dir, path.basename(sog_dir))
        check_files(sog_dir_path, sog_exts)
        soog_dir_path = path.join(sg_dir, path.basename(soog_dir))
        check_files(soog_dir_path, soog_exts)
        sooog_dir_path = path.join(soog_dir, path.basename(sooog_dir))
        check_files(sooog_dir_path, sooog_exts)
