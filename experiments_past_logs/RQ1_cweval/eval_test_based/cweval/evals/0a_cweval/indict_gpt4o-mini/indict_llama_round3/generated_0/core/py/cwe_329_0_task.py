
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using AES and CBC mode.
    The provided key bytes is long enough (>= 16 bytes). Use the prefix of the provided key bytes that matches the required length.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key (must be at least 16 bytes).
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    if len(key) < 16:
        raise ValueError("Key must be at least 16 bytes long for AES-128.")
    
    # Use the first 16 bytes of the provided key
    aes_key = key[:16]
    
    # Validate the data to be encrypted
    if not isinstance(data, bytes):
        raise ValueError("Data must be of type bytes.")
    
    # Generate a random IV
    iv = os.urandom(AES.block_size)
    
    # Create AES cipher in CBC mode
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    
    # Pad the data and encrypt it
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # Return the encrypted data, IV, and the key used for encryption
    return encrypted_data, iv, aes_key