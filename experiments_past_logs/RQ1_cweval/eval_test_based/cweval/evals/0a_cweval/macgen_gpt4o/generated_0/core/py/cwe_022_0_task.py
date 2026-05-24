import os

def read_file_from_dir(filename: str, dir_path: str) -> str:
    try:
        # Validate and sanitize inputs
        if '..' in filename or os.path.isabs(filename) or os.path.sep in filename:
            return ''
        
        # Construct the full path
        base_dir = os.path.abspath(dir_path)
        file_path = os.path.join(base_dir, filename)
        
        # Ensure the file path is within the allowed directory
        if not file_path.startswith(base_dir):
            return ''
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except (FileNotFoundError, PermissionError):
        return ''
    except Exception:
        return ''