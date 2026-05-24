
import os

def is_safe_path(base_path: str, user_path: str) -> bool:
    """
    Check if the user-supplied path is within the base directory.

    Args:
        base_path (str): The base directory path.
        user_path (str): The user-supplied path to check.

    Returns:
        bool: True if the user_path is within the base_path, False otherwise.
    """
    # Get the absolute paths
    base_path = os.path.abspath(base_path)
    user_path = os.path.abspath(user_path)

    # Check if the user_path starts with the base_path
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, user_path])

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
        # Construct the full file path
        file_path = os.path.join(dir_path, filename)

        # Validate the path to prevent directory traversal
        if not is_safe_path(dir_path, file_path):
            return ''
        
        # Check if the file exists and is a file
        if not os.path.isfile(file_path):
            return ''
        
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ''
    except PermissionError:
        return ''
    except Exception as e:
        # Log the exception if needed for debugging (not implemented here)
        return ''