
import os
import hashlib
from typing import List, Tuple


def hash_passwords(
    usernames: List[str], passwords: List[str]
) -> List[Tuple[bytes, bytes]]:
    '''
    Given a list of passwords of users, use hashlib.pbkdf2_hmac to hash them with SHA-256, salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

    Args:
        usernames: A list of usernames.
        passwords: A list of passwords of the users to hash.

    Returns:
        List[Tuple[bytes, bytes]]: A list of tuples containing the hashed passwords and the salts used for hashing.
    '''
    if len(usernames) != len(passwords):
        raise ValueError("The number of usernames must match the number of passwords.")
    
    hashed_passwords = []
    
    for username, password in zip(usernames, passwords):
        if not isinstance(username, str) or not isinstance(password, str):
            raise TypeError("Both username and password must be strings.")
        if not (1 <= len(username) <= 150):
            raise ValueError(f"Username '{username}' must be between 1 and 150 characters.")
        if not (8 <= len(password) <= 128):
            raise ValueError(f"Password for user '{username}' must be between 8 and 128 characters.")
        if not username.strip() or not password.strip():
            raise ValueError("Username and password cannot be empty or whitespace.")
        
        # Generate a random salt
        salt = os.urandom(32)  # 32 bytes for the salt
        # Hash the password using PBKDF2 HMAC with SHA-256
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            10000
        )
        # Append the tuple of (hashed_password, salt) to the list
        hashed_passwords.append((hashed_password, salt))
    
    return hashed_passwords