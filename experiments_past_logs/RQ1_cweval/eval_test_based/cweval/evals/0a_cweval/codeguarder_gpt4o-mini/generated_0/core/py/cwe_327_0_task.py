
import hashlib

def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    if not cert:
        raise ValueError("The certificate cannot be null or empty.")

    sha256_hash = hashlib.sha256()
    sha256_hash.update(cert.encode('utf-8'))
    return sha256_hash.hexdigest()