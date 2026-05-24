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
    if not os.path.isfile(tar_path) or not os.access(tar_path, os.R_OK):
        return False

    if not os.path.isdir(dest_path) or not os.access(dest_path, os.W_OK):
        return False

    max_file_size = 10 * 1024 * 1024  # 10 MB limit for individual files
    max_files_count = 1000  # Limit on the number of files to extract
    total_extracted_size = 0
    max_total_size = 100 * 1024 * 1024  # 100 MB limit for total extracted size

    try:
        with tarfile.open(tar_path, 'r') as tar:
            extracted_files_count = 0
            for member in tar.getmembers():
                if extracted_files_count >= max_files_count:
                    return False

                member_path = os.path.join(dest_path, member.name)

                # Security checks
                if '..' in member.name or os.path.isabs(member.name):
                    return False

                # Ensure the path is within the destination directory
                if not os.path.commonpath([member_path, dest_path]) == dest_path:
                    return False

                # Check for dangerous file types and sizes
                if member.isfile():
                    if member.size > max_file_size:
                        return False
                    total_extracted_size += member.size
                    if total_extracted_size > max_total_size:
                        return False

                # Check for symlinks and handle them
                if member.issym() or member.islnk():
                    continue  # Skip symlinks

                tar.extract(member, dest_path)
                extracted_files_count += 1
        return True
    except (FileNotFoundError, PermissionError, tarfile.TarError):
        return False