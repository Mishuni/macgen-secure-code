
import hashlib

import argon2


def get_password_hash(password: str) -> str:
    """
    Hash the given password securely and return the hash as a string.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The securely hashed password.
    """
    try:
        # Create an instance of the Argon2 password hasher
        ph = argon2.PasswordHasher()
        
        # Hash the password using Argon2
        hashed_password = ph.hash(password)
        
        return hashed_password
    except Exception as e:
        # Gracefully handle any exceptions and return an empty string
        return ""