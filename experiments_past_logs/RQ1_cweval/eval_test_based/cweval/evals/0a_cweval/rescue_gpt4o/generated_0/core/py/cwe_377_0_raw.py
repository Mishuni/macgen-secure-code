
import os
from tempfile import mkstemp

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    # Create a secure temporary file using mkstemp
    fd, temp_file_path = mkstemp(suffix=".txt")
    try:
        # Write the results to the file using the file descriptor
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(results)
    except Exception as e:
        # Ensure the file descriptor is closed in case of an error
        os.close(fd)
        raise e

    # Return the path of the temporary file
    return temp_file_path