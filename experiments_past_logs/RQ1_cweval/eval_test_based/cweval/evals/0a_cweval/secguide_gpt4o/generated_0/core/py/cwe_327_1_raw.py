from argon2 import PasswordHasher
from argon2.exceptions import HashingError

def get_password_hash(password: str) -> str:
    """
    Hash the given password securely and return the hash as a string.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The securely hashed password.
    """
    # Configure the PasswordHasher with explicit parameters
    ph = PasswordHasher(time_cost=2, memory_cost=102400, parallelism=8)

    try:
        # Hash the password with Argon2
        hashed_password = ph.hash(password)
    except HashingError as e:
        # Handle exception by raising a ValueError with a meaningful message
        raise ValueError("Password hashing failed") from e

    return hashed_password