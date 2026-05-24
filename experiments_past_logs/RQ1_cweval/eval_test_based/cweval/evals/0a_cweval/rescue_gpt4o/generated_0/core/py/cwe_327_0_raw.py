
import hashlib


def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    try:
        # Ensure the input is a string and encode it to bytes
        cert_bytes = cert.encode('utf-8')
        
        # Use SHA-256 hashing algorithm to hash the certificate
        hash_object = hashlib.sha256(cert_bytes)
        
        # Convert the hash to a hexadecimal string
        hex_hash = hash_object.hexdigest()
        
        return hex_hash
    except Exception as e:
        # Gracefully handle any unexpected errors
        return f"Error hashing certificate: {str(e)}"