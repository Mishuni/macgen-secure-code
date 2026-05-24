from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import os
import json
import hashlib

def create_private_key(passphrase: str = None, key_size: int = 2048) -> str:
    """
    Generate a private RSA key, export it using the PEM format, and return it as a string.

    Args:
        passphrase (str): Optional passphrase to encrypt the private key.
        key_size (int): The size of the RSA key to generate (default is 2048).

    Returns:
        str: The RSA private key in PEM format.
    """
    if key_size not in [2048, 3072, 4096]:
        raise ValueError("Invalid key size. Choose from 2048, 3072, or 4096 bits.")
    
    if passphrase and (len(passphrase) < 12 or not any(char.isdigit() for char in passphrase)):
        raise ValueError("Passphrase must be at least 12 characters long and contain at least one digit.")

    try:
        key = RSA.generate(key_size)
        private_key = key.export_key(format='PEM')

        if passphrase:
            salt = get_random_bytes(16)
            # Use PBKDF2 to derive a secure key from the passphrase
            derived_key = PBKDF2(passphrase, salt, dkLen=32, count=1000000)
            nonce = get_random_bytes(16)
            cipher = AES.new(derived_key, AES.MODE_GCM, nonce=nonce)
            encrypted_key, tag = cipher.encrypt_and_digest(private_key)

            secure_storage = {
                'salt': salt.hex(),
                'nonce': nonce.hex(),
                'encrypted_key': encrypted_key.hex(),
                'tag': tag.hex()
            }
            return json.dumps(secure_storage)

        return private_key.decode('utf-8')

    except ValueError as ve:
        raise RuntimeError("Value error during key generation: " + str(ve))
    except Exception as e:
        raise RuntimeError("An error occurred during key generation: " + str(e))