
import hashlib
from OpenSSL import crypto

def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    try:
        # Load the certificate in PEM format
        cert_bytes = open(cert, 'rb').read()
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert_bytes)

        # Get the DER encoded version of the certificate
        der_cert = crypto.dump_certificate(crypto.FILETYPE_ASN1, certificate)

        # Create a SHA-256 hash of the DER encoded certificate
        hash_object = hashlib.sha256(der_cert)
        return hash_object.hexdigest()
    except Exception as e:
        # Handle exceptions gracefully
        return str(e)