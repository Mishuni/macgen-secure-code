import os
import stat
import errno
import logging

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Validate directory and filename to prevent directory traversal
    if '..' in directory or '..' in filename or not os.path.isabs(directory):
        raise ValueError("Invalid directory or filename.")

    # Ensure the directory is within a safe location
    base_directory = os.path.abspath('/tmp')  # Change this to your safe base directory
    abs_directory = os.path.abspath(directory)
    if not abs_directory.startswith(base_directory):
        raise ValueError("Directory is not within the allowed base directory.")

    # Ensure the directory exists
    os.makedirs(abs_directory, exist_ok=True)

    # Construct the full file path
    file_path = os.path.join(abs_directory, filename)

    # Sanitize content to prevent injection attacks (if applicable)
    # Implement specific sanitization based on your use case if necessary

    # Use a secure method to create the file with the desired permissions
    try:
        # Create the file with exclusive access
        fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, 'w') as file:
            file.write(content)
    except FileExistsError:
        raise FileExistsError(errno.EEXIST, "File already exists.")
    except OSError as e:
        raise IOError(f"Failed to write to file: {e}")

    # Check and set directory permissions to restrict access
    dir_permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    os.chmod(abs_directory, dir_permissions)

    # Optionally, implement cleanup logic if needed