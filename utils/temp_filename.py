from tempfile import NamedTemporaryFile
def get_temp_filename(file) -> str:
    """Generate a temporary filename."""
    with NamedTemporaryFile(delete=False) as tmp_file:
        return tmp_file.name