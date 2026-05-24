from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
import os

def create_private_key() -> str:
    """
    Generate a private RSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The RSA private key in PEM format.
    """
    # Generate a new RSA key pair with a larger key size for enhanced security
    key = RSA.generate(3072)
    
    # Securely obtain a passphrase from an environment variable
    passphrase = os.environ.get('RSA_PASSPHRASE')
    if not passphrase:
        raise ValueError("Passphrase not found in environment variables.")
    
    # Export the private key in PEM format with AES-256 encryption
    private_key_pem = key.export_key(format='PEM', passphrase=passphrase, pkcs=8, protection="scryptAndAES256-CBC")
    
    # Return the private key as a string
    return private_key_pem.decode('utf-8')