""" Tests for gdipak

"""

import pytest
from gdipak import *

from os import path

class TestValidateArgs:
    def test_current_dir(self):
        args = dict([("in_dir", "."), ("out_dir", ".")])
        validate_args(args)

    def test_parent_dir(self):
        args = dict([("in_dir", ".."), ("out_dir", "..")])
        validate_args(args)

    def test_fully_qualified_dir(self):
        fqd = path.abspath(".")
        args = dict([("in_dir", fqd), ("out_dir", fqd)])
        validate_args(args)

