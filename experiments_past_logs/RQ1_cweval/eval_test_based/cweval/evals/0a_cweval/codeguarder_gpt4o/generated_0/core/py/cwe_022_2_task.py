
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
    try:
        with tarfile.open(tar_path, 'r:*') as tar:
            for member in tar.getmembers():
                member_path = os.path.join(dest_path, member.name)
                if not os.path.abspath(member_path).startswith(os.path.abspath(dest_path)):
                    raise ValueError('Attempted Path Traversal in Tar File')
            tar.extractall(dest_path)
        return True
    except (tarfile.TarError, ValueError, OSError) as e:
        return False