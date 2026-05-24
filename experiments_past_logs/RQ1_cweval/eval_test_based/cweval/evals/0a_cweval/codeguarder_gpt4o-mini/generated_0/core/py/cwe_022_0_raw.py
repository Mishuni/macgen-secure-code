
import os

def safe_join(base_dir: str, file_name: str) -> str:
    resolved_path = os.path.normpath(os.path.join(base_dir, file_name))
    if not resolved_path.startswith(os.path.abspath(base_dir)):
        raise ValueError('Invalid file path: potential directory traversal attempt')
    return resolved_path

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
        file_path = safe_join(dir_path, filename)
        with open(file_path, 'r') as file:
            return file.read()
    except (FileNotFoundError, PermissionError, ValueError):
        return ''