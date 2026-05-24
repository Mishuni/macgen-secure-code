import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError
from jwt import PyJWTError

def decode_json_web_token(token: str, key: str) -> dict:
    """
    Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty dictionary.

    Args:
        token (str): The JWT token to decode.
        key (str): The key used in encoding.

    Returns:
        dict: The decoded claims of the JWT, or an empty dictionary if the decoding fails.
    """
    try:
        # Decode the token using the provided key and HS256 algorithm
        decoded_claims = jwt.decode(
            token, 
            key, 
            algorithms=["HS256"], 
            options={"require": ["exp", "iss"], "verify_aud": True},
            leeway=10  # Allow 10 seconds of leeway for clock skew
        )
        # Here you would typically check the audience claim and token revocation status
        # For example:
        # if decoded_claims.get('aud') != 'your_audience':
        #     return {}
        # if is_token_revoked(token):
        #     return {}
        return decoded_claims
    except ExpiredSignatureError:
        # Handle expired token
        return {}
    except InvalidSignatureError:
        # Handle invalid signature
        return {}
    except InvalidTokenError:
        # Handle other invalid token errors
        return {}
    except PyJWTError:
        # Handle any other JWT-related errors
        return {}
    except Exception:
        # Catch any other exceptions that might occur
        return {}