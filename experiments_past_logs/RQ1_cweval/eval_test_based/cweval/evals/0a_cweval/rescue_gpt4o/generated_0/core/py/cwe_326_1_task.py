
from Crypto.PublicKey import DSA

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Generate a DSA key with a secure key length of 2048 bits
    key = DSA.generate(2048)
    
    # Export the private key in PEM format
    private_key_pem = key.export_key(format='PEM').decode('utf-8')
    
    # Return the private key as a string
    return private_key_pem