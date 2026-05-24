import os
import binascii
import bcrypt

def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    # Generate a random salt using bcrypt
    salt = bcrypt.gensalt()

    # Hash the certificate using bcrypt with the generated salt
    hashed = bcrypt.hashpw(cert.encode('utf-8'), salt)

    # Return the salt and hashed certificate as a hexadecimal string
    return f"{binascii.hexlify(salt).decode('utf-8')}:{binascii.hexlify(hashed).decode('utf-8')}"