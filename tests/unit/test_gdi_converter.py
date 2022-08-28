
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

    def test_file_path_as_path(self, tmp_path):
        """Test passing a Path object as the file_path."""
        gdi_converter = GdiConverter(tmp_path)
        assert gdi_converter.file_path == str(tmp_path)

    def test_file_path_as_str(self, tmp_path):
        """Test passing a str object as the file_path."""
        gdi_converter = GdiConverter(str(tmp_path))
        assert gdi_converter.file_path == str(tmp_path)

    def test_file_contents(self):
        """Test passing file_contents."""
        contents = "We've been trying to reach you about your car's extended warranty."
        gdi_converter = GdiConverter(file_contents=contents)
        assert gdi_converter.file_contents == contents

    def test_convert_file_without_file_name(self):
        """Tests failure mode when the file is not defined."""
        gdi_converter = GdiConverter(file_contents="Content")
        with pytest.raises(ValueError) as ex:
            gdi_converter.convert_file()
        assert "Cannot convert file, file_path is None" in str(ex.value)

    def test_convert_file_contents_without_file_contents(self, tmp_path):
        """Tests failure mode when the file is not defined."""
        gdi_converter = GdiConverter(file_path=tmp_path)
        with pytest.raises(ValueError) as ex:
            gdi_converter.convert_file_contents(gdi_converter.file_contents)
        assert (
            "file_contents should be a string representing the contents of a GDI file"
            in str(ex.value)
        )

    # pylint disable=protected-access
    def test__backup_file(self, tmp_path):
        """Test backing up the source file."""
        file_name = "original.gdi"
        file_contents = "Naked as the eyes of a clown"
        file_path = (tmp_path / file_name)
        file_path.write_text(file_contents)
        gdi_converter = GdiConverter(file_path)
        gdi_converter._backup_file(file_contents)
        backup_file = tmp_path / (file_name + ".bak")
        assert backup_file.exists()
        assert gdi_converter.backup_exists
        assert backup_file.read_text() == file_contents

    # pylint disable=protected-access
    def test__delete_backup_exist_state_set(self, tmp_path):
        """Test removing the backup file"""
        file_name = "original.gdi"
        file_path = (tmp_path / file_name)
        gdi_converter = GdiConverter(file_path)
        gdi_converter.backup_exists = True
        backup_path = tmp_path / gdi_converter.backup_file_path
        backup_path.touch()
        gdi_converter._delete_backup()
        assert not backup_path.exists()

    # pylint disable=protected-access
    def test__delete_backup_exist_state_not_set(self, tmp_path):
        """Test removing the backup file"""
        file_name = "original.gdi"
        file_path = (tmp_path / file_name)
        gdi_converter = GdiConverter(file_path)
        backup_path = tmp_path / gdi_converter.backup_file_path
        backup_path.touch()
        gdi_converter._delete_backup()
        assert backup_path.exists()

    def test_convert_gdi(self, tmpdir, gdi_file):
        """Tests converting a GDI file into the output format."""
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
