
from Crypto.PublicKey import DSA
from Crypto.Random import get_random_bytes
from Crypto.Util.number import getPrime
from Crypto.PublicKey.DSA import DSAParameterNumbers

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Generate secure DSA parameters
    p = getPrime(2048, randfunc=get_random_bytes)
    q = getPrime(256, randfunc=get_random_bytes)
    g = pow(2, (p - 1) // q, p)

    # Create DSA parameter numbers
    dsa_params = DSAParameterNumbers(p, q, g)

    # Generate the DSA key
    key = DSA.generate(2048, randfunc=get_random_bytes)

    # Export the private key in PEM format
    private_key_pem = key.export_key(format='PEM')

    return private_key_pem.decode('utf-8')