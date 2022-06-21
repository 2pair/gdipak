""" tests for the argument parser"""

import pytest
from os import path
from argparse import ArgumentParser

from gdipak.argparser import ArgParser
from gdipak.argparser import RecursiveMode


class TestRecursiveMode:
    def test_preserve_structure(self):
        mode = RecursiveMode.make(0)
        assert mode == RecursiveMode.PRESERVE_STRUCTURE

    def test_flat_structure(self):
        mode = RecursiveMode.make(1)
        assert mode == RecursiveMode.FLAT_STRUCTURE

    def test_invalid(self):
        with pytest.raises(ValueError):
            RecursiveMode.make(2)


class TestArgs:
    a = ArgParser("0")

    def test_setup_argparser(self):
        ap = self.a._ArgParser__setup_argparser()
        assert type(ap) is ArgumentParser

    def test_parse_version(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-v"])

    def test_valid_out_dir(self):
        ap = self.a._ArgParser__setup_argparser()
        parsed = ap.parse_args(["-d", ".", "-o", "./out"])
        assert parsed.in_dir == "."
        assert parsed.out_dir == "./out"
        assert parsed.modify is False
        assert parsed.namefile is False
        assert parsed.recursive is None

    def test_valid_modify(self):
        ap = self.a._ArgParser__setup_argparser()
        parsed = ap.parse_args(["-d", ".", "-m"])
        assert parsed.out_dir is None
        assert parsed.modify is True

    def test_valid_namefile(self):
        ap = self.a._ArgParser__setup_argparser()
        parsed = ap.parse_args(["-d", ".", "-m", "-n"])
        assert parsed.namefile is True

    def test_valid_recursive_default(self):
        ap = self.a._ArgParser__setup_argparser()
        parsed = ap.parse_args(["-d", ".", "-m", "-r"])
        assert parsed.recursive == 0

    def test_valid_recursive_ints(self):
        ap = self.a._ArgParser__setup_argparser()
        parsed = ap.parse_args(["-d", ".", "-m", "-r", "0"])
        assert parsed.recursive == 0
        parsed = ap.parse_args(["-d", ".", "-m", "-r", "1"])
        assert parsed.recursive == 1
        parsed = ap.parse_args(["-d", ".", "-m", "-r", "333"])
        assert parsed.recursive == 333

    def test_invalid_missing_in_dir_arg(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-o", "./out"])

    def test_invalid_missing_in_dir_val(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-d", "-o", "./out"])

    def test_invalid_missing_out_dir_val(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-d", ".", "-o"])

    def test_invalid_out_dir_modify(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-d", ".", "-o", "./out", "-m"])

    def test_invalid_recursive(self):
        ap = self.a._ArgParser__setup_argparser()
        with pytest.raises(SystemExit):
            ap.parse_args(["-d", ".", "-m", "-r", "recursive please!"])


class TestValidateArgs:
    a = ArgParser("0")
    base_args = {
        "in_dir": None,
        "out_dir": None,
        "modify": None,
        "recursive": None,
        "namefile": None,
    }

    def test_current_dir(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": "."})
        self.a._ArgParser__validate_args(args)

    def test_parent_dir(self):
        args = self.base_args
        args.update({"in_dir": "..", "out_dir": ".."})
        self.a._ArgParser__validate_args(args)

    def test_fully_qualified_dir(self):
        fqd = path.abspath(".")
        args = self.base_args
        args.update({"in_dir": fqd, "out_dir": fqd})
        self.a._ArgParser__validate_args(args)

    def test_invalid_in_dir(self):
        args = self.base_args
        args.update({"in_dir": 7, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_missing_in_dir(self, tmpdir):
        args = self.base_args
        args.update({"in_dir": tmpdir + "/fake_dir", "out_dir": "."})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_file_as_in_dir(self, tmpdir):
        f = tmpdir.join("a file")
        f.write("")
        args = self.base_args
        args.update({"in_dir": f, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_none_in_dir(self):
        args = self.base_args
        args.update({"in_dir": None, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_invalid_out_dir(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": "U:/RuhRoh"})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_none_out_dir(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": None})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_non_existent_out_dir(self, tmpdir):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": tmpdir + "/fake_dir"})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_file_as_out_dir(self, tmpdir):
        f = tmpdir.join("a file")
        f.write("")
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": f})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_recursive_valid(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 0})
        self.a._ArgParser__validate_args(args)

        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 1})
        self.a._ArgParser__validate_args(args)

    def test_recursive_invalid(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 27})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": "Houston"})
        with pytest.raises(SystemExit):
            self.a._ArgParser__validate_args(args)

    def test_recursive_and_modify(self):
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 1, "modify": True})
        args = self.a._ArgParser__validate_args(args)
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE


class TestRun:
    def test_run_out_dir_recursive(self):
        a = ArgParser("0")
        args = a.run(["-d", ".", "-o", "..", "-r"])
        assert args["in_dir"] == "."
        assert args["out_dir"] == ".."
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE
        assert args["modify"] is False
        assert args["namefile"] is False

    def test_run_modify_namefile(self):
        a = ArgParser("0")
        args = a.run(["-d", ".", "-m", "-n"])
        assert args["in_dir"] == "."
        assert args["modify"] is True
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE
        assert args["namefile"] is True
        assert args["out_dir"] is None
