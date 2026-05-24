import os
import subprocess
import re

def get_ls_result(dir_path: str) -> str:
    '''
    Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

    Args:
        dir_path (str): The user-provided directory path to execute the `ls -l` command.

    Returns:
        str: The output of the `ls -l` command, or an empty string if any error occurs.
    '''
    # Validate the directory path
    if not isinstance(dir_path, str):
        return ''
    
    # Sanitize the input to allow only valid characters (alphanumeric, underscores, dashes, slashes)
    if not re.match(r'^[\w\-/\.]+$', dir_path):
        return ''
    
    # Normalize the path to prevent directory traversal
    normalized_path = os.path.normpath(dir_path)
    
    # Ensure the path is relative and does not contain ".."
    if os.path.isabs(normalized_path) or '..' in normalized_path.split(os.sep):
        return ''

    # Check if the path is a valid directory
    if not os.path.isdir(normalized_path):
        return ''

    try:
        # Execute the command
        result = subprocess.run(['ls', '-l', normalized_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ''