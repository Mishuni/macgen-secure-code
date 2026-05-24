import os
from tempfile import NamedTemporaryFile

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    try:
        with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(results)
            temp_file_name = temp_file.name

        # Set restrictive permissions to the file
        os.chmod(temp_file_name, 0o600)

        return temp_file_name
    except Exception as e:
        raise