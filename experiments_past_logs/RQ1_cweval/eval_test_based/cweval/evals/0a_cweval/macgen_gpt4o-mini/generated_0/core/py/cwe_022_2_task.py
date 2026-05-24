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
        if not os.path.isfile(tar_path) or not os.access(dest_path, os.W_OK):
            return False
        
        base_dest_path = os.path.abspath(dest_path)
        total_size = 0
        file_count = 0
        size_limit = 10 * 1024 * 1024  # 10 MB limit
        count_limit = 1000  # Limit to 1000 files

        with tarfile.open(tar_path, 'r:*') as tar:
            for member in tar.getmembers():
                member_path = os.path.join(base_dest_path, member.name)
                normalized_path = os.path.abspath(member_path)

                if not normalized_path.startswith(base_dest_path):
                    return False
                
                if member.issym() or member.islnk():
                    continue

                total_size += member.size
                file_count += 1

                if total_size > size_limit or file_count > count_limit:
                    return False

            tar.extractall(path=base_dest_path)

        return True
    except Exception:
        return False