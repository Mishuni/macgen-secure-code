
import os
import errno

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Ensure the directory exists
    try:
        os.makedirs(directory, mode=0o700, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Construct the full file path
    file_path = os.path.join(directory, filename)

    # Open the file securely and write the content
    try:
        with open(file_path, 'x', encoding='utf-8') as f:
            f.write(content)
        # Set file permissions to be accessible only by the current user
        os.chmod(file_path, 0o600)
    except FileExistsError:
        raise FileExistsError(f"The file '{file_path}' already exists.")
    except Exception as e:
        raise IOError(f"An error occurred while writing to the file: {e}")