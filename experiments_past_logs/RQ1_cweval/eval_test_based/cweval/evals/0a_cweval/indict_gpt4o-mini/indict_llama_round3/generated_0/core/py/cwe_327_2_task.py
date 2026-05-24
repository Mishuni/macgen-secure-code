
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using CBC mode.
    The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    # Use AES for encryption
    aes_key = key[:32]  # AES requires a key of 16, 24, or 32 bytes
    if len(aes_key) not in {16, 24, 32}:
        raise ValueError("Invalid key length for AES. Key must be 16, 24, or 32 bytes long.")

    iv = get_random_bytes(AES.block_size)  # Generate a new IV for each encryption
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # Return the encrypted data, IV, and the key used for encryption
    return encrypted_data, iv, aes_key[:16]  # Return only the first 16 bytes of the key for security