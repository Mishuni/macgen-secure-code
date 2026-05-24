from Crypto.PublicKey import DSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
from typing import Tuple

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Generate a 2048-bit DSA key
    key = DSA.generate(2048)
    
    # Use a user-provided passphrase or securely store the passphrase if it needs to be reused
    passphrase = b'user_provided_passphrase'  # This should be securely obtained from the user
    
    # Generate a random salt
    salt = get_random_bytes(16)
    
    # Derive a key using PBKDF2
    key_encryption_key = PBKDF2(passphrase, salt, dkLen=32, count=1000000)
    
    # Use AES-GCM for authenticated encryption
    cipher = AES.new(key_encryption_key, AES.MODE_GCM)
    iv = cipher.nonce
    
    # Encrypt the private key
    encrypted_key, tag = cipher.encrypt_and_digest(pad(key.export_key(format='DER'), AES.block_size))
    
    # Encode the encrypted key, iv, salt, and tag in base64 for safe storage
    encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')
    iv_b64 = base64.b64encode(iv).decode('utf-8')
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    tag_b64 = base64.b64encode(tag).decode('utf-8')
    
    # Return the encrypted key, iv, salt, and tag as a single string
    return f"{encrypted_key_b64}:{iv_b64}:{salt_b64}:{tag_b64}"