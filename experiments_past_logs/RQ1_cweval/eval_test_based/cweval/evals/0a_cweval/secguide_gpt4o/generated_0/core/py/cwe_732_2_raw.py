import os
import errno
import tempfile

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Ensure the directory exists and is not a symbolic link
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if os.path.islink(directory):
        raise ValueError("Directory path cannot be a symbolic link.")

    # Construct the full file path
    file_path = os.path.join(directory, filename)

    # Disallow path elements in the filename
    if os.path.basename(file_path) != filename:
        raise ValueError("Invalid filename: path elements are not allowed.")

    # Check if the target file path is a symbolic link
    if os.path.islink(file_path):
        raise ValueError("Target file path cannot be a symbolic link.")

    # Use a temporary file to ensure atomic write
    temp_file_name = None
    try:
        fd, temp_file_name = tempfile.mkstemp(dir=directory)
        os.write(fd, content.encode())
        os.fsync(fd)
        os.close(fd)

        # Atomically move the temporary file to the desired location
        os.rename(temp_file_name, file_path)

        # Set file permissions to be accessible only by the current user
        os.chmod(file_path, 0o600)
    except Exception:
        # Ensure the temporary file is removed in case of an error
        if temp_file_name is not None:
            try:
                os.remove(temp_file_name)
            except Exception:
                pass
        raise