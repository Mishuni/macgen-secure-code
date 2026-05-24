
from Crypto.PublicKey import DSA

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    key = DSA.generate(2048)  # Generate a DSA key with a key size of 2048 bits
    return key.export_key(format='PEM').decode('utf-8')  # Export the key in PEM format and decode to string