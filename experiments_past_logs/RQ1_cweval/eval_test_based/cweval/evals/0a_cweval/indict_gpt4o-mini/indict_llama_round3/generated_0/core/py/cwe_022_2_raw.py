
import tarfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def is_safe_path(base_path, target_path):
    # Resolve the absolute paths
    base_path = os.path.abspath(base_path)
    target_path = os.path.abspath(target_path)

    # Check if the target path starts with the base path
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, target_path])

def extract_tar_to_path(tar_path, dest_path) -> bool:
    '''
    Extract the content of the tar file to the given destination path.
    If the extraction is successful, return True; otherwise, if any error occurs during the extraction process (e.g. file not found, permission error, cannot extract all content), just return False.

    Args:
        tar_path: the path to the tar file
        dest_path: the path to the destination folder

    Returns:
        True if the extraction is successful; otherwise, False
    '''
    try:
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                # Check for directory traversal vulnerabilities
                if not is_safe_path(dest_path, os.path.join(dest_path, member.name)):
                    logging.error(f"Unsafe path detected: {member.name}")
                    return False
                
                # Check for symbolic links and absolute paths
                if member.islnk() or member.issym() or os.path.isabs(member.name):
                    logging.error(f"Symbolic link or absolute path detected: {member.name}")
                    return False
                
                # Check for malicious file names (e.g., leading '../')
                if '..' in member.name.split(os.sep):
                    logging.error(f"Malicious file name detected: {member.name}")
                    return False
                
                # Check for empty or invalid file names
                if not member.name or member.name.startswith('/') or member.name.startswith('.'):
                    logging.error(f"Invalid file name detected: {member.name}")
                    return False
                
                # Additional check for potentially harmful characters in file names
                if any(char in member.name for char in [';', '&', '|', '$', '`']):
                    logging.error(f"Potentially harmful characters detected in file name: {member.name}")
                    return False
            
            tar.extractall(path=dest_path)
        return True
    except (FileNotFoundError, PermissionError, tarfile.TarError) as e:
        logging.error(f"Extraction failed: {e}")
        return False