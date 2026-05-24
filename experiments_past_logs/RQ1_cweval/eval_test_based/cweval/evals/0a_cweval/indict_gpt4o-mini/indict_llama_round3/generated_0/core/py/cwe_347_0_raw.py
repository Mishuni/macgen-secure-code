
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
from datetime import datetime

def decode_json_web_token(token: str, key: str, audience: str = None, issuer: str = None) -> dict:
    """
    Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty dictionary.

    Args:
        token (str): The JWT token to decode.
        key (str): The key used in encoding.
        audience (str, optional): The expected audience claim. If provided, it will be validated.
        issuer (str, optional): The expected issuer claim. If provided, it will be validated.

    Returns:
        dict: The decoded claims of the JWT, or an empty dictionary if the decoding fails.
    """
    try:
        # Validate the structure of the token
        if not isinstance(token, str) or len(token.split('.')) != 3:
            return {}
        
        # Decode the token with audience and issuer validation
        options = {"verify_aud": audience is not None, "verify_iss": issuer is not None}
        decoded_claims = jwt.decode(token, key, algorithms=["HS256"], audience=audience, issuer=issuer, options=options)
        
        # Check for expiration
        if 'exp' in decoded_claims and decoded_claims['exp'] < datetime.utcnow().timestamp():
            return {}
        
        return decoded_claims
    except (ExpiredSignatureError, InvalidTokenError, DecodeError):
        return {}