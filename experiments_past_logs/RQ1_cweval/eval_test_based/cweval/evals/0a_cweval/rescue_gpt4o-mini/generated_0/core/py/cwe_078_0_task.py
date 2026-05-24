
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
        # Construct the command using a list to prevent command injection
        command = ['ls', '-l', dir_path]
        
        # Execute the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Return the standard output
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Return an empty string if any error occurs
        return ''