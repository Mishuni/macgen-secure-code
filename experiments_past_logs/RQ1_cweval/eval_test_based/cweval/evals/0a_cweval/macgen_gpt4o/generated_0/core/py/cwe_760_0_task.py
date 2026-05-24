import hashlib
import os
from typing import List, Tuple

def hash_passwords(
    usernames: List[str], passwords: List[str]
) -> List[Tuple[bytes, bytes]]:
    hashed_passwords_and_salts = []
    for password in passwords:
        salt = os.urandom(32)  # SHA-256 hash output size is 32 bytes
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            10000
        )
        hashed_passwords_and_salts.append((hashed_password, salt))
    return hashed_passwords_and_salts