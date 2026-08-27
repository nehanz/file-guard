import os
import pytest
from app.utils.file_utils import get_file_extension, ensure_upload_dir_exists

def test_file_extension_extraction():
    assert get_file_extension("document.pdf") == ".pdf"
    assert get_file_extension("IMAGE.PNG") == ".png"
    assert get_file_extension("archive.tar.gz") == ".gz"
    assert get_file_extension("no_extension") == ""
    
def test_directory_creation():
    test_dir = "tests/test_uploads"
    ensure_upload_dir_exists(test_dir)
    assert os.path.exists(test_dir)
    assert os.path.isdir(test_dir)
    # Cleanup
    os.rmdir(test_dir)
