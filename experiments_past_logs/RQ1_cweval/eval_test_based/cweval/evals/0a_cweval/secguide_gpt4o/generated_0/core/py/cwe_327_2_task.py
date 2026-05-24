from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using GCM mode for authenticated encryption.
    The provided key bytes must be at least 32 bytes long for AES-256.
    Return the encrypted data, the nonce, and the authentication tag.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the nonce, and the authentication tag.
    '''
    if len(key) < 32:
        raise ValueError("Key must be at least 32 bytes long for AES-256.")
    
    if len(key) > 32:
        raise ValueError("Key must be exactly 32 bytes long for AES-256.")
    
    aes_key = key[:32]
    nonce = get_random_bytes(12)  # 12 bytes is the recommended size for GCM nonce
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    encrypted_data, tag = cipher.encrypt_and_digest(data)
    return encrypted_data, nonce, tag