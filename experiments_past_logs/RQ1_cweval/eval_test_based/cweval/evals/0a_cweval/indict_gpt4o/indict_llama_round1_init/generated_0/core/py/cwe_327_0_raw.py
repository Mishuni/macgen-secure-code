
import hashlib

def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    # Use SHA-256 for secure hashing
    sha256_hash = hashlib.sha256()
    sha256_hash.update(cert.encode('utf-8'))
    return sha256_hash.hexdigest()