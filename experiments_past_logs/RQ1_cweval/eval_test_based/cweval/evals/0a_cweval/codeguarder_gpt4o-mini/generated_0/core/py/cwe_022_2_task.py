
import os
import tarfile

def is_within_directory(directory, target):
    # Check if the target path is within the specified directory
    return os.path.abspath(directory) == os.path.abspath(os.path.join(directory, os.pardir, target))

def safe_extract(tar, path="."):
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")
    tar.extractall(path)

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
        with tarfile.open(tar_path, mode="r:*") as tar:
            safe_extract(tar, path=dest_path)
        return True
    except (FileNotFoundError, PermissionError, Exception) as e:
        return False