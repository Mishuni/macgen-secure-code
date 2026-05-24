import os
import re

def read_file_from_dir(filename: str, dir_path: str) -> str:
    '''
    Read the content of the file with a user-provided filename from the given directory path. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string.

    Args:
        filename (str): The name of the file to read, requested by a user.
        dir_path (str): The directory path where the file is located.

    Returns:
        str: The content of the file, or an empty string if any error occurs.
    '''
    # Allowlist of acceptable file extensions
    allowed_extensions = {'.txt', '.md', '.csv'}

    # Validate filename using a refined regular expression
    if not re.match(r'^[\w-]+(\.[\w-]+)?$', filename):
        return ''

    # Check if the file extension is allowed
    _, ext = os.path.splitext(filename)
    if ext not in allowed_extensions:
        return ''

    # Canonicalize the directory path
    safe_dir_path = os.path.realpath(dir_path)

    # Ensure the directory path ends with a separator
    if not safe_dir_path.endswith(os.sep):
        safe_dir_path += os.sep

    # Construct the full file path and canonicalize it
    file_path = os.path.abspath(os.path.join(safe_dir_path, filename))

    # Ensure the file path starts with the safe directory path to prevent directory traversal
    if not file_path.startswith(safe_dir_path):
        return ''

    # Check if any part of the path is a symbolic link
    if any(os.path.islink(os.path.join(safe_dir_path, part)) for part in file_path[len(safe_dir_path):].split(os.sep)):
        return ''

    try:
        # Open the file securely
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except (FileNotFoundError, PermissionError, OSError):
        return ''