
from tempfile import NamedTemporaryFile
import os

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    with NamedTemporaryFile(delete=False) as tmp_file:
        try:
            tmp_file.write(results.encode('utf-8'))
            return tmp_file.name
        except Exception as e:
            os.unlink(tmp_file.name)  # Clean up the file if an error occurs
            raise e