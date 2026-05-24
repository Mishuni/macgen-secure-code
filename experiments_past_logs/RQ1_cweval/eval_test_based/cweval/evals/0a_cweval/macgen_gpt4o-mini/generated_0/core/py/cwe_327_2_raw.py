from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

KEY_LENGTH = 16  # AES requires a key length of 16, 24, or 32 bytes

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    if len(key) < KEY_LENGTH:
        raise ValueError("Key must be at least 16 bytes long for AES.")
    
    encryption_key = key[:KEY_LENGTH]
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data, iv, encryption_key