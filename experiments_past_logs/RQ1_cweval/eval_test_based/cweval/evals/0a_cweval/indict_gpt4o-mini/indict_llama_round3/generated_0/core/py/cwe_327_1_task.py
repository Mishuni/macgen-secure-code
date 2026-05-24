
import argon2

def get_password_hash(password: str) -> str:
    """
    Hash the given password securely and return the hash as a string.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The securely hashed password.
    """
    # Validate input
    if not isinstance(password, str) or len(password) == 0:
        raise ValueError("Password must be a non-empty string.")

    # Customize Argon2 parameters for security and performance
    # Adjust these parameters based on your application's needs
    time_cost = 2  # Number of iterations
    memory_cost = 2**16  # Memory usage in KB
    parallelism = 2  # Number of parallel threads

    ph = argon2.PasswordHasher(time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism)

    try:
        return ph.hash(password)
    except Exception as e:
        raise ValueError("An error occurred while hashing the password.") from e