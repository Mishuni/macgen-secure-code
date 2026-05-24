
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
        # Validate and sanitize inputs
        if not filename or not dir_path:
            return ''
        
        # Prevent directory traversal attacks
        if any(sep in filename for sep in ('..', '/', '\\')) or filename.startswith(('/', '\\')):
            return ''
        
        file_path = os.path.join(dir_path, filename)
        
        # Ensure the path is within the specified directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(dir_path) + os.sep):
            return ''
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except (FileNotFoundError, PermissionError, OSError, IsADirectoryError, UnicodeDecodeError):
        return ''