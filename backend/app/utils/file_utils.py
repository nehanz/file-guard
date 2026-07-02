import os
import hashlib
from typing import BinaryIO

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file efficiently by reading in chunks."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 64kb chunks
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_extension(filename: str) -> str:
    """Extract and lowercase file extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower()

def ensure_upload_dir_exists(directory: str) -> None:
    """Ensure the target upload directory exists."""
    os.makedirs(directory, exist_ok=True)
