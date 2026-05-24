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
        # Validate the tar_path
        if not os.path.isfile(tar_path):
            return False

        # Validate the dest_path
        if not os.path.isdir(dest_path):
            return False

        with tarfile.open(tar_path, 'r') as tar:
            abs_dest_path = os.path.abspath(dest_path)

            def is_within_directory(directory, target):
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
                return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

            for member in tar.getmembers():
                member_path = os.path.join(dest_path, member.name)
                if not is_within_directory(abs_dest_path, member_path):
                    return False

            tar.extractall(dest_path)
        return True
    except tarfile.TarError:
        return False
    except Exception:
        return False