
from random import randint
import string
import pytest

from gdipak.gdi_converter import GdiConverter
from tests.utils import GdiGenerator


@pytest.fixture()
def gdi_file():
    """Generates a random GDI file and associated metadata."""
    charset = string.ascii_letters + string.digits + string.punctuation + " "
    name = ""
    for _ in range(randint(10, 128)):
        name += charset[randint(0, len(charset) - 1)]
    yield GdiGenerator(name)()


class TestGdiConverter:
    """Tests converting the contents of the GDI file."""
    def test_missing_args(self):
        """Test passing no arguments during instantiation."""
        with pytest.raises(ValueError) as ex:
            GdiConverter()
        assert "Either file_path or file_contents must be defined." in str(ex.value)

    def test_too_many_args(self):
        """Test passing both arguments during instantiation."""
        with pytest.raises(ValueError) as ex:
            GdiConverter(file_path="/root", file_contents="~~missing~~")
        assert (
            "Only one of file_path or file_contents can be defined." in str(ex.value)
        )

    def test_convert_gdi(self, tmpdir, gdi_file):
        """Tests converting a GDI file into the output format"""
        file_content = gdi_file[0]
        file_metadata = gdi_file[1]
        file_name = file_metadata["name"].replace("/", "_")
        file_path = tmpdir.join(file_name)
        with open(file_path, "w"):
            file_path.write(file_content)
        gdi_converter = GdiConverter(file_path=file_path)
        gdi_converter.convert_file()
        # TODO: Finish writing this test. Need to parse the contents I guess...
        # TODO: Maybe see about generalizing the other parser that validates the
        # TODO: Generated GDI.
