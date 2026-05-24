
import os
import tarfile
from typing import Optional


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
        # Ensure the tar_path exists and is a file
        if not os.path.isfile(tar_path):
            return False

        # Ensure the destination path exists and is a directory
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)
        elif not os.path.isdir(dest_path):
            return False

        # Open the tar file securely
        with tarfile.open(tar_path, 'r:*') as tar:
            # Iterate through each member in the tar file
            for member in tar.getmembers():
                # Sanitize the file path to prevent directory traversal
                member_path = os.path.join(dest_path, member.name)
                if not os.path.commonpath([dest_path, os.path.abspath(member_path)]).startswith(os.path.abspath(dest_path)):
                    return False

            # Extract all members to the destination directory
            tar.extractall(path=dest_path)

        return True
    except (tarfile.TarError, OSError, IOError):
        # Catch any errors related to tar file operations or file system issues
        return False