import argon2
import re
from time import time

def get_password_hash(password: str) -> str:
    """
    Hash the given password securely using Argon2 and return the hash as a string.

    Args:
        password (str): The password to be hashed. Must meet complexity requirements.

    Returns:
        str: The securely hashed password.

    Raises:
        ValueError: If the password does not meet complexity requirements.
        RuntimeError: If an error occurs while hashing the password.
    """
    # Validate password complexity
    if len(password) < 12:  # Minimum length requirement
        raise ValueError("Password must be at least 12 characters long.")
    if not re.search(r"[A-Z]", password):  # At least one uppercase letter
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):  # At least one lowercase letter
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):  # At least one digit
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # At least one special character
        raise ValueError("Password must contain at least one special character.")

    # Initialize PasswordHasher with configurable parameters
    ph = argon2.PasswordHasher(time_cost=2, memory_cost=2**16, parallelism=2)

    # Rate limiting mechanism (example: limit to 5 attempts per minute)
    # This is a placeholder for actual implementation
    # Implement your rate limiting logic here

    try:
        return ph.hash(password)
    except argon2.exceptions.HashingError as e:
        raise RuntimeError("An error occurred while hashing the password.") from e