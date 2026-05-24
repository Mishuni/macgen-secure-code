
from Crypto.PublicKey import RSA

def create_private_key() -> str:
    """
    Generate a private RSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The RSA private key in PEM format.
    """
    # Generate a 2048-bit RSA key
    key = RSA.generate(2048)
    
    # Export the key in PEM format and decode it to a string
    private_key_pem = key.exportKey('PEM').decode('utf-8')
    
    # Return the private key as a string
    return private_key_pem