from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using AES and GCM mode.
    The provided key bytes must be at least 32 bytes long. The key will be derived using PBKDF2.
    Return the encrypted data, the IV (initialization vector), and the salt.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the salt.
    '''
    if key is None or len(key) < 32:
        raise ValueError("Key must be at least 32 bytes long.")

    # Derive a strong encryption key using PBKDF2
    salt = get_random_bytes(16)  # Generate a random salt
    encryption_key = PBKDF2(key, salt, dkLen=32, count=100000)

    # Generate a random IV (nonce) for GCM mode
    iv = get_random_bytes(12)  # Recommended size for GCM nonce

    # Create AES cipher in GCM mode
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=iv)

    # Encrypt the data
    encrypted_data, tag = cipher.encrypt_and_digest(data)

    return encrypted_data, iv, salt  # Return the encrypted data, IV, and salt