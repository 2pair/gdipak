"""end to end functional tests"""

from os import path
from utils import make_files, check_files

import gdipak
import pdb
class TestGdiPak:
    def test_recursive_dir_different_out_dir_mode_zero(self, tmpdir, monkeypatch):
        sg_dir, _1 = make_files(tmpdir, "some game")
        sog_dir, _1 = make_files(sg_dir, "some other game")
        soog_dir, _1 = make_files(sg_dir, "some other other game")
        sooog_dir, _1 = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        #pdb.set_trace()
        monkeypatch.setattr("gdipak.argv", 
            ["pytest", "-d", str(sg_dir), "-o", str(out_dir),
            "-r", "0"])
        gdipak.main()

        dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(dir_path)
        dir_path = path.join(out_dir, path.basename(sog_dir))
        check_files(dir_path)
        dir_path = path.join(out_dir, path.basename(soog_dir))
        check_files(dir_path)
        dir_path = path.join(out_dir, path.basename(sooog_dir))
        check_files(dir_path)

    def test_recursive_dir_different_out_dir_mode_one(self, tmpdir, monkeypatch):
        sg_dir, _1 = make_files(tmpdir, "some game")
        sog_dir, _1 = make_files(sg_dir, "some other game")
        soog_dir, _1 = make_files(sg_dir, "some other other game")
        sooog_dir, _1 = make_files(soog_dir, "some other other other game")
        out_dir = tmpdir.mkdir("processed_game")
        
        monkeypatch.setattr("gdipak.argv", 
            ["pytest", "-d", str(sg_dir), "-o", str(out_dir),
            "-r", "1", "-n"])
        gdipak.main()

        sg_dir_path = path.join(out_dir, path.basename(sg_dir))
        check_files(sg_dir_path)
        sog_dir_path = path.join(sg_dir_path, path.basename(sog_dir))
        check_files(sog_dir_path)
        soog_dir_path = path.join(sg_dir_path, path.basename(soog_dir))
        check_files(soog_dir_path)
        sooog_dir_path = path.join(soog_dir_path, path.basename(sooog_dir))
        check_files(sooog_dir_path)
