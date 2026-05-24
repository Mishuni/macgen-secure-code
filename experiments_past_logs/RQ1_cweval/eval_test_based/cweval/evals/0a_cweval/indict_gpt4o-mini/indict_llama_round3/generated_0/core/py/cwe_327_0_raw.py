
import hashlib
import os
import base64

def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    # Input validation: Ensure the certificate is a non-empty string
    if not isinstance(cert, str) or not cert:
        raise ValueError("Certificate must be a non-empty string.")

    # Generate a random salt
    salt = os.urandom(16)

    # Create a SHA-256 hash object and update it with the salt and certificate
    sha256_hash = hashlib.sha256()
    sha256_hash.update(salt + cert.encode('utf-8'))

    # Combine the salt and the hash for storage
    salted_hash = salt + sha256_hash.digest()

    # Return the hexadecimal representation of the salt and hash
    return (salt + sha256_hash.digest()).hex()

def verify_certificate(cert: str, hashed_cert: str) -> bool:
    """
    Verify the given certificate against a previously hashed certificate.

    Args:
        cert (str): The original certificate to verify.
        hashed_cert (str): The previously hashed certificate (hexadecimal).

    Returns:
        bool: True if the certificate matches the hash, False otherwise.
    """
    # Decode the hexadecimal encoded hash
    salted_hash = bytes.fromhex(hashed_cert)

    # Extract the salt from the salted hash
    salt = salted_hash[:16]
    original_hash = salted_hash[16:]

    # Create a new hash with the same salt and the provided certificate
    sha256_hash = hashlib.sha256()
    sha256_hash.update(salt + cert.encode('utf-8'))

    # Compare the newly computed hash with the original hash in constant time
    return hashlib.compare_digest(original_hash, sha256_hash.digest())