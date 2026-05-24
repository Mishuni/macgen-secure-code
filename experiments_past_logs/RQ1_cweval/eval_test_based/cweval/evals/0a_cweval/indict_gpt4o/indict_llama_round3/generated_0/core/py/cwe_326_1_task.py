
from Crypto.PublicKey import DSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import os

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Generate a DSA private key
    key = DSA.generate(2048)
    private_key_pem = key.export_key(format='PEM')

    # Securely derive an AES key using a password and a unique salt
    password = os.environ.get('DSA_KEY_PASSWORD', 'default_secure_password').encode()
    salt = get_random_bytes(16)
    key_derived = PBKDF2(password, salt, dkLen=32, count=1000000)
    cipher = AES.new(key_derived, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(private_key_pem)

    # Encode the encrypted key, nonce, salt, and tag in base64 for safe storage
    encrypted_key = base64.b64encode(cipher.nonce + salt + tag + ciphertext).decode('utf-8')

    # Return the encrypted private key
    return encrypted_key