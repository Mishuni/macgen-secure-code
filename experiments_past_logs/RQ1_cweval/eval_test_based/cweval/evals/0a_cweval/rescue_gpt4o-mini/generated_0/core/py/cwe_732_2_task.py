
import os
import stat

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Sanitize and validate the directory and filename inputs
    if not os.path.isdir(directory):
        raise ValueError("The specified directory does not exist or is not a directory.")
    
    # Ensure the filename is safe
    if os.path.basename(filename) != filename:
        raise ValueError("The filename contains invalid characters or path traversal.")
    
    # Construct the full path for the file
    file_path = os.path.join(directory, filename)

    # Write the content to the file
    with open(file_path, 'w') as secret_file:
        secret_file.write(content)

    # Set the file permissions to be accessible only by the current user
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)