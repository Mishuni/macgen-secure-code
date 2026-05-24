from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes]:
    '''
    Encrypt the data with the key using AES and GCM mode.
    The provided key bytes must be at least 32 bytes long for AES-256 encryption.
    Return the encrypted data and the nonce used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes]: The encrypted data and the nonce used for encryption.
    '''
    if len(key) < 32:
        raise ValueError("Key must be at least 32 bytes long for AES-256 encryption.")
    
    # Use the first 32 bytes of the key for AES-256 encryption
    aes_key = key[:32]
    
    # Create a new AES cipher in GCM mode with a unique nonce
    nonce = get_random_bytes(12)  # 12 bytes is a recommended size for GCM nonce
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    
    # Encrypt the data
    encrypted_data, tag = cipher.encrypt_and_digest(data)
    
    return encrypted_data, nonce