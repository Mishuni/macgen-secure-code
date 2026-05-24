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
    if not isinstance(filename, str) or not isinstance(dir_path, str):
        return ''
    
    # Validate filename to prevent directory traversal attacks using regex
    if not re.match(r'^[\w\-. ]+$', filename):
        return ''
    
    full_path = os.path.abspath(os.path.join(dir_path, filename))
    
    if not os.path.isfile(full_path) or not os.access(full_path, os.R_OK):
        return ''
    
    try:
        with open(full_path, 'r') as file:
            return file.read()
    except (FileNotFoundError, PermissionError):
        return ''