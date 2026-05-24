
import os

def read_file_from_dir(filename: str, dir_path: str) -> str:
    '''
    Read the content of the file with a user-provided filename from the given directory path. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string.

    Args:
        filename (str): The name of the file to read, requested by a user.
        dir_path (str): The directory path where the file is located.

    Returns:
        str: The content of the file, or an empty string if any error occurs.
    '''
    try:
        # Ensure the directory path is absolute and normalized
        dir_path = os.path.abspath(dir_path)

        # Ensure the filename is sanitized to prevent directory traversal
        sanitized_filename = os.path.basename(filename)

        # Construct the full file path
        file_path = os.path.join(dir_path, sanitized_filename)

        # Verify the file path is within the intended directory
        if not file_path.startswith(dir_path + os.sep):
            return ""

        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    except (OSError, IOError):
        # Return an empty string if any error occurs
        return ""