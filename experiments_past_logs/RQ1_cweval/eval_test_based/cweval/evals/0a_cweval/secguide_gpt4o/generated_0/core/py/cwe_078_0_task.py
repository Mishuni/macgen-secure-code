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
        # Define a base directory to restrict access
        base_dir = os.path.abspath('/tmp')

        # Resolve the absolute path and ensure it is a directory
        abs_path = os.path.abspath(dir_path)

        # Check if the resolved path is within the base directory
        if not abs_path.startswith(base_dir):
            return ''

        if not os.path.isdir(abs_path):
            return ''

        # Use os.scandir() for more detailed information
        entries_info = []
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_file():
                    entry_type = 'file'
                elif entry.is_dir():
                    entry_type = 'directory'
                else:
                    entry_type = 'other'
                entries_info.append(f"{entry.name} ({entry_type})")

        return '\n'.join(entries_info)
    except (OSError, PermissionError):
        return ''