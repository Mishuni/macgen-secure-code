import jwt
from jwt.exceptions import InvalidTokenError

def decode_json_web_token(token: str, key: str) -> dict:
    try:
        decoded = jwt.decode(token, key, algorithms=["HS256"], options={"verify_exp": True, "verify_iss": True})
        return decoded
    except InvalidTokenError:
        return {}