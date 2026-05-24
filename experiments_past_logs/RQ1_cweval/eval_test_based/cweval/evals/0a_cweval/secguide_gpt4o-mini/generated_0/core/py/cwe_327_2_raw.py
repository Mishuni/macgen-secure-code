from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
import os
import hashlib

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes]:
    '''
    Encrypt the data with the key using AES in CBC mode.
    The provided key bytes must be 16, 24, or 32 bytes long. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
    Return the encrypted data and the IV (initialization vector).

    Args:
        key (bytes): The bytes to generate the encryption key (must be 16, 24, or 32 bytes long).
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes]: The encrypted data and the IV.
    
    Raises:
        ValueError: If the key length is not valid.
    '''
    if len(key) not in {16, 24, 32}:
        raise ValueError("Key must be 16, 24, or 32 bytes long.")
    
    # Use the first 16 bytes for AES-128
    aes_key = key[:16]
    
    # Generate a random IV
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    
    # Pad the data
    padded_data = pad(data, AES.block_size)
    
    # Encrypt the data
    encrypted_data = cipher.encrypt(padded_data)
    
    # Prepend the IV to the encrypted data
    return iv + encrypted_data