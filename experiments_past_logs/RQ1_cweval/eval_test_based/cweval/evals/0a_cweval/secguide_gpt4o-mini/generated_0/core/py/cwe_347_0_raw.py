import jwt
import os
import logging
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError

def decode_json_web_token(token: str, key: str) -> dict:
    """
    Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty dictionary.

    Args:
        token (str): The JWT token to decode.
        key (str): The key used in encoding.

    Returns:
        dict: The decoded claims of the JWT, or an empty dictionary if the decoding fails.
    """
    issuer = os.getenv('JWT_ISSUER')
    audience = os.getenv('JWT_AUDIENCE')
    
    if issuer is None or audience is None:
        logging.warning("JWT_ISSUER or JWT_AUDIENCE environment variable not set.")
        return {}

    if not isinstance(token, str) or len(token.split('.')) != 3:
        return {}

    try:
        decoded_claims = jwt.decode(token, key, algorithms=["HS256"], options={"require": ["iss", "aud"]})

        if 'iss' not in decoded_claims or decoded_claims['iss'] != issuer:
            return {}
        if 'aud' not in decoded_claims or decoded_claims['aud'] != audience:
            return {}

        return decoded_claims
    except ExpiredSignatureError:
        return {}
    except InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")
        return {}
    except DecodeError as e:
        logging.error(f"Decode error: {e}")
        return {}