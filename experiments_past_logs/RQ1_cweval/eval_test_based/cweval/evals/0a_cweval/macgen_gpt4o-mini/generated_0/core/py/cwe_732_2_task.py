import os
import stat
import re

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    if not re.match(r'^[\w\-. ]+$', filename):
        raise ValueError("Invalid filename")
    
    if '..' in directory or not os.path.isabs(directory):
        raise ValueError("Invalid directory")
    
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except (OSError, FileNotFoundError, PermissionError):
        raise
    
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)