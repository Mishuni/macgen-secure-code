
import subprocess
import os

def get_ls_result(dir_path: str) -> str:
    '''
    Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

    Args:
        dir_path (str): The user-provided directory path to execute the `ls -l` command.

    Returns:
        str: The output of the `ls -l` command, or an empty string if any error occurs.
    '''
    try:
        # Ensure the directory path is safe and exists
        if not os.path.isdir(dir_path):
            return ""

        # Use subprocess to execute the command securely
        result = subprocess.check_output(['ls', '-l', dir_path], universal_newlines=True)
        return result
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        return ""