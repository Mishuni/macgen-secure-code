
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using AES and CBC mode.
    The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    # AES requires a key length of 16, 24, or 32 bytes. We'll use 32 bytes for AES-256.
    aes_key = key[:32]  # Use the first 32 bytes of the provided key
    iv = os.urandom(AES.block_size)  # Generate a random IV for CBC mode
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)  # Create a new AES cipher object
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))  # Encrypt the data with padding

    return encrypted_data, iv, aes_key