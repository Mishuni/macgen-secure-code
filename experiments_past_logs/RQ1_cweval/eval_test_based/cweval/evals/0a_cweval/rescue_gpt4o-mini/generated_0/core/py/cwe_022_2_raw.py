
import os
import tarfile
import tempfile
import shutil

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
        # Create a temporary directory to extract the tar file
        temp_dir = tempfile.mkdtemp()
        
        # Open the tar file
        with tarfile.open(tar_path, 'r') as tar:
            # Extract all contents to the temporary directory
            tar.extractall(path=temp_dir)
        
        # Move extracted files to the destination path
        for item in os.listdir(temp_dir):
            s = os.path.join(temp_dir, item)
            d = os.path.join(dest_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)
        
        return True
    except Exception as e:
        # Log the exception if needed (not implemented here)
        return False
    finally:
        # Clean up the temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)