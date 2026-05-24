
import os
import tarfile

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
    def is_within_directory(directory, target):
        # Ensure the target path is within the specified directory
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
        return os.path.commonpath([abs_directory, abs_target]) == abs_directory

    try:
        if not os.path.exists(tar_path) or not tarfile.is_tarfile(tar_path):
            return False

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                member_path = os.path.join(dest_path, member.name)
                if not is_within_directory(dest_path, member_path):
                    return False
            tar.extractall(path=dest_path, members=[
                member for member in tar.getmembers() 
                if is_within_directory(dest_path, os.path.join(dest_path, member.name))
            ])
        return True
    except (tarfile.TarError, OSError):
        return False