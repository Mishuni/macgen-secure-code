
from Crypto.PublicKey import DSA
import logging
import os
import secrets

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    try:
        # Generate a DSA key of 2048 bits using a secure random number generator
        key = DSA.generate(2048, randfunc=secrets.token_bytes)  
        
        # Export the key in PEM format
        private_key_pem = key.export_key(format='PEM')  
        
        # Return the PEM string without storing it in a temporary file
        return private_key_pem.decode('utf-8')  
    except Exception as e:
        logging.error("An error occurred while generating the DSA private key: %s", e)
        raise