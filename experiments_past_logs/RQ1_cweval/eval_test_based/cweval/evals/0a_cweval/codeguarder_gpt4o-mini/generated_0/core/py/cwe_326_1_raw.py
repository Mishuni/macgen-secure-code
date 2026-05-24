
from Crypto.PublicKey import DSA
from Crypto.Random import get_random_bytes
from Crypto.Util import number
import os

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Securely generate a DSA key with a recommended key size of 2048 bits
    key = DSA.generate(2048, get_random_bytes)

    # Export the private key in PEM format
    private_key_pem = key.export_key(format='PEM')

    return private_key_pem.decode('utf-8')