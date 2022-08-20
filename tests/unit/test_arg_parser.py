""" tests for the argument parser"""

from argparse import ArgumentParser
from os import path
import pytest

from gdipak.arg_parser import ArgParser, RecursiveMode


class TestRecursiveMode:
    """Tests recursive mode enum."""

    def test_preserve_structure(self):
        """Test preserve structure mapping."""
        mode = RecursiveMode(0)
        assert mode == RecursiveMode.PRESERVE_STRUCTURE

    def test_flatten_structure(self):
        """Test flat structure mapping."""
        mode = RecursiveMode(1)
        assert mode == RecursiveMode.FLATTEN_STRUCTURE

    def test_invalid(self):
        """Test invalid enum value."""
        with pytest.raises(ValueError):
            RecursiveMode(2)


class TestArgs:
    """Tests the argument parser."""

    # pylint: disable=protected-access
    @classmethod
    def setup_class(cls):
        """Test class setup method."""
        cls.arg_parser = ArgParser("0")

    def test_setup_argparser(self):
        """Test setup argparser."""
        arg_parser = self.arg_parser._ArgParser__setup()
        assert isinstance(arg_parser, ArgumentParser)

    def test_parse_version(self):
        """Test parsing version string."""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-v"])

    def test_valid_out_dir(self):
        """Test setting optional output directory argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        parsed = arg_parser.parse_args(["-i", ".", "-o", "./out"])
        assert parsed.in_dir == "."
        assert parsed.out_dir == "./out"
        assert parsed.modify is False
        assert parsed.namefile is False
        assert parsed.recursive is None

    def test_valid_modify(self):
        """Test setting optional modify argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        parsed = arg_parser.parse_args(["-i", ".", "-m"])
        assert parsed.out_dir is None
        assert parsed.modify is True

    def test_valid_namefile(self):
        """Test setting optional namefile argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        parsed = arg_parser.parse_args(["-i", ".", "-m", "-n"])
        assert parsed.namefile is True

    def test_valid_recursive_default(self):
        """Test default recursive argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        parsed = arg_parser.parse_args(["-i", ".", "-m", "-r"])
        assert parsed.recursive == 0

    def test_valid_recursive_ints(self):
        """Tests setting optional recursive mode argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        parsed = arg_parser.parse_args(["-i", ".", "-m", "-r", "0"])
        assert parsed.recursive == 0
        parsed = arg_parser.parse_args(["-i", ".", "-m", "-r", "1"])
        assert parsed.recursive == 1
        parsed = arg_parser.parse_args(["-i", ".", "-m", "-r", "333"])
        assert parsed.recursive == 333

    def test_invalid_missing_in_dir_arg(self):
        """Test not setting the input directory argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-o", "./out"])

    def test_invalid_missing_in_dir_val(self):
        """Test not passing a value for the input directory argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-i", "-o", "./out"])

    def test_invalid_missing_out_dir_val(self):
        """Test not passing a value for the output directory argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-i", ".", "-o"])

    def test_invalid_out_dir_modify(self):
        """Test passing both an output directory argument and a modify argument."""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-i", ".", "-o", "./out", "-m"])

    def test_invalid_recursive(self):
        """Test passing an invalid data type to the recursive argument"""
        arg_parser = self.arg_parser._ArgParser__setup()
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-i", ".", "-m", "-r", "recursive please!"])


class TestValidateArgs:
    """Tests validating arguments in the argument parser."""

    # pylint: disable=protected-access
    @classmethod
    def setup_class(cls):
        """Test class setup method."""
        cls.arg_parser = ArgParser("0")
        cls.base_args = {
            "in_dir": None,
            "out_dir": None,
            "modify": None,
            "recursive": None,
            "namefile": None,
        }

    def test_current_dir(self):
        """Test that the current directory is valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": "."})
        self.arg_parser._ArgParser__validate_args(args)

    def test_parent_dir(self):
        """Test that the parent directory is valid."""
        args = self.base_args
        args.update({"in_dir": "..", "out_dir": ".."})
        self.arg_parser._ArgParser__validate_args(args)

    def test_fully_qualified_dir(self):
        """Test that the fully qualified directory path is valid."""
        fqd = path.abspath(".")
        args = self.base_args
        args.update({"in_dir": fqd, "out_dir": fqd})
        self.arg_parser._ArgParser__validate_args(args)

    def test_invalid_in_dir(self):
        """Test that something that isn't a directory is not valid."""
        args = self.base_args
        args.update({"in_dir": 7, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_nonexistent_in_dir(self, tmpdir):
        """Test that a nonexistent directory is not valid."""
        args = self.base_args
        args.update({"in_dir": tmpdir + "/fake_dir", "out_dir": "."})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_file_as_in_dir(self, tmpdir):
        """Test that a file name is not valid."""
        file = tmpdir.join("a file")
        file.write("")
        args = self.base_args
        args.update({"in_dir": file, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_none_in_dir(self):
        """Test that 'None' is not valid."""
        args = self.base_args
        args.update({"in_dir": None, "out_dir": "."})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_invalid_out_dir(self):
        """Test that something that isn't a directory is not valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": "U:/RuhRoh"})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_none_out_dir(self):
        """Test that 'None' is not valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": None})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_nonexistent_out_dir(self, tmpdir):
        """Test that a nonexistent directory is not valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": tmpdir + "/fake_dir"})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_file_as_out_dir(self, tmpdir):
        """Test that a file name is not valid."""
        file = tmpdir.join("a file")
        file.write("")
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": file})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_recursive_valid(self):
        """Test recursive modes are valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 0})
        self.arg_parser._ArgParser__validate_args(args)

        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 1})
        self.arg_parser._ArgParser__validate_args(args)

    def test_recursive_invalid(self):
        """Test things that aren't recursive modes are not valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 27})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": "Houston"})
        with pytest.raises(SystemExit):
            self.arg_parser._ArgParser__validate_args(args)

    def test_recursive_and_modify(self):
        """Test recursive with modify is valid."""
        args = self.base_args
        args.update({"in_dir": ".", "out_dir": ".", "recursive": 1, "modify": True})
        args = self.arg_parser._ArgParser__validate_args(args)
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE


class TestRun:
    """Test running the argument parser"""

    def test_run_out_dir_recursive(self):
        """Test with a given out directory and the recursive flag."""
        arg_parser = ArgParser("0")
        args = arg_parser(["-i", ".", "-o", "..", "-r"])
        assert args["in_dir"] == "."
        assert args["out_dir"] == ".."
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE
        assert args["modify"] is False
        assert args["namefile"] is False

    def test_run_modify_namefile(self):
        """Test with a the modify flag and the namefile flag."""
        arg_parser = ArgParser("0")
        args = arg_parser(["-i", ".", "-m", "-n"])
        assert args["in_dir"] == "."
        assert args["modify"] is True
        assert args["recursive"] == RecursiveMode.PRESERVE_STRUCTURE
        assert args["namefile"] is True
        assert args["out_dir"] is None
