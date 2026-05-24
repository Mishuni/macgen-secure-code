
import subprocess

def get_ls_result(dir_path: str) -> str:
    '''
    Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

    Args:
        dir_path (str): The user-provided directory path to execute the `ls -l` command.

    Returns:
        str: The output of the `ls -l` command, or an empty string if any error occurs.
    '''
    try:
        # Use subprocess.run with structured arguments to securely execute the command
        result = subprocess.run(
            ['ls', '-l', dir_path],  # Structured argument list
            text=True,               # Ensure output is returned as a string
            capture_output=True,     # Capture stdout and stderr
            check=True               # Raise an exception if the command fails
        )
        return result.stdout  # Return only the stdout
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        # Gracefully handle errors and return an empty string
        return ""