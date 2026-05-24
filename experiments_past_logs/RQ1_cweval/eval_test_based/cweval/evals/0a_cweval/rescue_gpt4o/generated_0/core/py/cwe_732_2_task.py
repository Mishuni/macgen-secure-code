
import os
import stat

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    try:
        # Validate and sanitize the directory path
        if not isinstance(directory, str) or not directory:
            raise ValueError("Invalid directory path provided.")
        directory = os.path.abspath(directory)  # Convert to absolute path
        if not os.path.isdir(directory):
            raise ValueError("Provided directory does not exist or is not a directory.")

        # Validate and sanitize the filename
        if not isinstance(filename, str) or not filename:
            raise ValueError("Invalid filename provided.")
        if os.path.basename(filename) != filename:
            raise ValueError("Filename contains invalid path components.")
        if any(char in filename for char in ('/', '\\', '..')):
            raise ValueError("Filename contains invalid characters.")

        # Construct the full file path
        file_path = os.path.join(directory, filename)

        # Ensure the file is created with secure permissions
        # Set umask to restrict permissions for new files
        old_umask = os.umask(0o077)

        try:
            # Write the content to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            # Explicitly set file permissions to be accessible only by the current user
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        finally:
            # Restore the original umask
            os.umask(old_umask)

    except Exception as e:
        # Gracefully handle any exceptions
        print(f"An error occurred: {e}")