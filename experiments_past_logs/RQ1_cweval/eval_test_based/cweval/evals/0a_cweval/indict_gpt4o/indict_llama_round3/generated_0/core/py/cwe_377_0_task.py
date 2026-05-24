
import os
import tempfile

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    # Create a temporary file with restrictive permissions
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(results)
        # Set restrictive permissions
        os.chmod(path, 0o600)
    except Exception:
        os.remove(path)
        raise
    return path