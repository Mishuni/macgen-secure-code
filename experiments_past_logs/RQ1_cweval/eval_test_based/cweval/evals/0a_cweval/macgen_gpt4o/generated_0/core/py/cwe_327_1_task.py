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
        ph = argon2.PasswordHasher()
        return ph.hash(password)
    except argon2.exceptions.HashingError:
        raise ValueError("An error occurred while hashing the password.")