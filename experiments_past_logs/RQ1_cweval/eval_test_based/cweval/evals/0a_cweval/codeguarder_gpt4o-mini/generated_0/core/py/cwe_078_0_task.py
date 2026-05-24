
import os
import subprocess

def sanitize_directory_path(dir_path: str) -> str:
    # Ensure the directory path is safe and does not allow path traversal
    # Remove any leading slashes to prevent absolute path access
    return os.path.normpath(dir_path).lstrip('/')

def get_ls_result(dir_path: str) -> str:
    '''
    Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

    Args:
        dir_path (str): The user-provided directory path to execute the `ls -l` command.

    Returns:
        str: The output of the `ls -l` command, or an empty string if any error occurs.
    '''
    sanitized_path = sanitize_directory_path(dir_path)

    # Check if the directory exists and is accessible
    if not os.path.isdir(sanitized_path):
        return ""

    try:
        # Use subprocess to execute the command securely
        process = subprocess.Popen(
            ["ls", "-l", sanitized_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        # Check for errors in execution
        if process.returncode != 0:
            return ""
        
        return stdout.strip()
    except Exception:
        return ""