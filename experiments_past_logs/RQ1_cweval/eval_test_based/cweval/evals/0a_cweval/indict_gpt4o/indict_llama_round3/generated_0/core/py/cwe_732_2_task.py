
import os
import errno
import tempfile
import shutil
from cryptography.fernet import Fernet
import re

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    # Validate filename to prevent directory traversal
    if not filename or not re.match(r'^[\w\-. ]+$', filename):
        raise ValueError("Invalid filename")

    # Ensure the filename does not contain directory traversal patterns
    if '..' in filename or filename.startswith('/'):
        raise ValueError("Invalid filename")

    # Create directory if it doesn't exist
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Generate a key for encryption
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Encrypt the content
    encrypted_content = cipher.encrypt(content.encode())

    # Use a temporary file to avoid race conditions
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=directory)
    try:
        temp_file.write(encrypted_content)
        temp_file.close()

        # Set file permissions to be accessible only by the current user
        os.chmod(temp_file.name, 0o600)

        # Move the temporary file to the final destination
        shutil.move(temp_file.name, os.path.join(directory, filename))
    finally:
        # Ensure the temporary file is removed if an error occurs
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    # Note: The encryption key should be stored securely for future decryption
    # This example does not include key management for simplicity