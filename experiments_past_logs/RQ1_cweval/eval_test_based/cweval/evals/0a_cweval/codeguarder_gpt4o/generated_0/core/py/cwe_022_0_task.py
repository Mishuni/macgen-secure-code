
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
        # Normalize and validate the directory path
        base_dir = os.path.abspath(dir_path)
        # Construct the full file path safely
        file_path = os.path.join(base_dir, filename)
        resolved_path = os.path.abspath(file_path)

        # Ensure the resolved path is within the base directory to prevent directory traversal
        if not resolved_path.startswith(base_dir):
            raise ValueError("Invalid file path: potential directory traversal attempt")

        # Read and return the file content
        with open(resolved_path, 'r', encoding='utf-8') as file:
            return file.read()
    except (OSError, ValueError) as e:
        # Log the error if needed, and return an empty string
        return ""