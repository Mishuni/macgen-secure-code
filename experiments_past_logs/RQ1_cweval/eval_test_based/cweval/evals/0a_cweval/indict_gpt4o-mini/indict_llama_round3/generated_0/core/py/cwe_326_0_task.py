
from Crypto.PublicKey import RSA
import logging

def create_private_key() -> str:
    """
    Generate a private RSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The RSA private key in PEM format.
    """
    try:
        # Generate a new RSA key pair
        key = RSA.generate(2048)
        private_key_pem = key.export_key(format='PEM')

        # Log the action for auditing purposes
        logging.info("RSA private key generated successfully.")

        # Return the private key in PEM format
        return private_key_pem.decode('utf-8')
    
    except ValueError as ve:
        logging.error("Value error occurred while generating the RSA private key: %s", ve)
        raise RuntimeError("Value error occurred while generating the RSA private key.") from ve
    
    except Exception as e:
        logging.error("An unexpected error occurred while generating the RSA private key: %s", e)
        raise RuntimeError("An unexpected error occurred while generating the RSA private key.") from e