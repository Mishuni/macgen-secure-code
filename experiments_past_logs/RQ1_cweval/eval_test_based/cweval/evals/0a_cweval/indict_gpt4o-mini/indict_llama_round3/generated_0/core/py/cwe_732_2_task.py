
import os
import stat
import tempfile
import shutil

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Validate the directory
    if not os.path.isdir(directory):
        raise ValueError(f"The directory '{directory}' does not exist.")
    
    # Normalize and validate the filename to prevent directory traversal attacks
    if not filename or os.path.isabs(filename) or '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Invalid filename. It must be a relative path and cannot contain '..' or path separators.")
    
    # Create the full path for the file
    file_path = os.path.join(directory, filename)

    # Ensure the directory is writable
    if not os.access(directory, os.W_OK):
        raise PermissionError(f"No write permission for the directory '{directory}'.")

    # Use a temporary file to avoid race conditions
    temp_file_path = os.path.join(directory, f".{filename}.tmp")

    # Write the content to the temporary file
    try:
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(content)
    except Exception as e:
        raise IOError(f"Failed to write to temporary file '{temp_file_path}': {e}")

    # Set the file permissions to be accessible only by the current user
    try:
        os.chmod(temp_file_path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
        raise IOError(f"Failed to set permissions for temporary file '{temp_file_path}': {e}")

    # Move the temporary file to the final destination
    try:
        shutil.move(temp_file_path, file_path)
    except Exception as e:
        raise IOError(f"Failed to move temporary file to '{file_path}': {e}")

    # Set permissions again for the final file to ensure they are correct
    try:
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
        raise IOError(f"Failed to set permissions for file '{file_path}': {e}")