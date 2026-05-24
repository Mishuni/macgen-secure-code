import hashlib
import os
import base64
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
        raise ValueError("Usernames and passwords lists must be of the same length.")

    hashed_passwords = []
    for password in passwords:
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string.")
        
        salt = os.urandom(32)  # Generate a random 32-byte salt
        hashed = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000  # Use a higher number of iterations
        )
        # Append the raw bytes of hashed password and salt
        hashed_passwords.append((hashed, salt))
    return hashed_passwords