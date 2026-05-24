import hashlib

def hash_certificate(cert: str) -> str:
    cert_bytes = cert.encode('utf-8')
    hash_object = hashlib.sha256()
    hash_object.update(cert_bytes)
    return hash_object.hexdigest()