
import os
import stat
import errno

def is_safe_directory(directory: str) -> bool:
    """Check if the directory is safe and accessible."""
    normalized_dir = os.path.normpath(directory)
    if not os.path.isdir(normalized_dir):
        return False
    # Ensure the directory is not a parent directory
    if os.path.abspath(normalized_dir) != normalized_dir:
        return False
    return True

def validate_filename(filename: str) -> bool:
    """Validate the filename to ensure it does not contain unsafe characters."""
    return all(c.isalnum() or c in ('_', '-', '.') for c in filename)

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    if not is_safe_directory(directory):
        raise ValueError("Invalid or unsafe directory provided.")
    
    if not validate_filename(filename):
        raise ValueError("Invalid filename provided.")

    full_path = os.path.join(directory, filename)

    try:
        with open(full_path, 'w') as secret_file:
            secret_file.write(content)
        # Set file permissions to be accessible only by the current user
        os.chmod(full_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError as e:
        if e.errno == errno.EACCES:
            raise PermissionError("Permission denied while trying to write the file.")
        else:
            raise