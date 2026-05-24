import os

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Invalid filename")
    if not os.path.isdir(directory):
        raise ValueError("Invalid directory")
    
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        os.chmod(file_path, 0o600)
    except (OSError, FileNotFoundError, PermissionError) as e:
        raise e