import hashlib
import os
from typing import List, Tuple


def hash_passwords(
    usernames: List[str], passwords: List[str]
) -> List[Tuple[bytes, bytes]]:
    if any(len(username) < 3 or len(username) > 30 or not username.isalnum() for username in usernames):
        raise ValueError("Invalid username: must be 3-30 characters long and alphanumeric.")
    
    results = []
    for password in passwords:
        if not (8 <= len(password) <= 128):
            raise ValueError("Password must be between 8 and 128 characters.")
        salt = os.urandom(32)
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 10000
        )
        results.append((hashed_password, salt))
    return results