from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from os import urandom

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
    if len(key) < 64:
        raise ValueError("Key must be at least 64 bytes long.")
    
    key = key[:32]  # Use the first 32 bytes for AES-256
    iv = urandom(AES.block_size)  # Generate a secure random IV
    
    # Ensure data is padded correctly
    padded_data = pad(data, AES.block_size)  # Pad the data
    
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)  # Create AES cipher in CBC mode
        encrypted_data = cipher.encrypt(padded_data)  # Encrypt the data
    except Exception:
        raise ValueError("Encryption failed")
    
    return encrypted_data, iv, key  # Return encrypted data, IV, and key