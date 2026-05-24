
import argon2

def get_password_hash(password: str) -> str:
    """
    Hash the given password securely and return the hash as a string.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The securely hashed password.
    """
    ph = argon2.PasswordHasher()
    try:
        return ph.hash(password)
    except argon2.exceptions.HashingError as e:
        raise RuntimeError("An error occurred while hashing the password.") from e