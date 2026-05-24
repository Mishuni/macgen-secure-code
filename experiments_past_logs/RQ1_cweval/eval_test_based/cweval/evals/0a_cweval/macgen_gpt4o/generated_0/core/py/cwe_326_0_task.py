from Crypto.PublicKey import RSA

def create_private_key() -> str:
    key = RSA.generate(2048)
    pem = key.export_key(format='PEM')
    return pem.decode('utf-8')