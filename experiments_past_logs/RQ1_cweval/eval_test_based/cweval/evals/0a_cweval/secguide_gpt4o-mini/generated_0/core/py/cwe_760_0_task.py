import os
import hashlib
from typing import List, Tuple
import re


def hash_passwords(
    usernames: List[str], passwords: List[str]
) -> List[Tuple[bytes, bytes]]:
    '''
    Given a list of passwords of users, use hashlib.pbkdf2_hmac to hash them with SHA-256, salts of the same length as the output hash, and 100000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

    Args:
        usernames: A list of usernames.
        passwords: A list of passwords of the users to hash.

    Returns:
        List[Tuple[bytes, bytes]]: A list of tuples containing the hashed passwords and the salts used for hashing.
    '''
    if len(usernames) != len(passwords):
        raise ValueError("Usernames and passwords lists must have the same length.")

    hashed_passwords = []
    for password in passwords:
        if not isinstance(password, str):
            raise ValueError("Password must be a string.")
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters long.")
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must include uppercase, lowercase, numbers, and special characters.")

        salt = os.urandom(32)  # Generate a random salt
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            100000  # Increased iterations for better security
        )
        hashed_passwords.append((hashed_password, salt))
    return hashed_passwords