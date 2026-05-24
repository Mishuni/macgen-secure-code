
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using GCM mode.
    The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    # Use AES-GCM for authenticated encryption
    aes_key = key[:32]  # Use the first 32 bytes for AES-256
    cipher = AES.new(aes_key, AES.MODE_GCM)
    iv = cipher.nonce
    encrypted_data, tag = cipher.encrypt_and_digest(pad(data, AES.block_size))
    return encrypted_data + tag, iv, aes_key