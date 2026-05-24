
import hashlib
import os
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
    try:
        # Ensure the input lists are of the same length
        if len(usernames) != len(passwords):
            raise ValueError("The number of usernames and passwords must match.")

        hashed_data = []
        for password in passwords:
            # Generate a random salt of the same length as the hash output (32 bytes for SHA-256)
            salt = os.urandom(32)
            # Hash the password using pbkdf2_hmac with SHA-256, the generated salt, and 10000 iterations
            hashed_password = hashlib.pbkdf2_hmac(
                'sha256',  # Hashing algorithm
                password.encode('utf-8'),  # Convert password to bytes
                salt,  # Salt
                10000  # Number of iterations
            )
            # Append the hashed password and salt as a tuple to the result list
            hashed_data.append((hashed_password, salt))

        return hashed_data

    except Exception as e:
        # Gracefully handle any unexpected errors
        print(f"An error occurred: {e}")
        return []