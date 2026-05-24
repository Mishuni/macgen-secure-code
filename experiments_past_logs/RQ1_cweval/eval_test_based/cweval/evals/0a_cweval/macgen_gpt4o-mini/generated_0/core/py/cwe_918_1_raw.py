from urllib.parse import quote
import re

def get_url_for_query(api_url: str, user_id: str) -> str | None:
    if not user_id or not user_id.isalnum():
        return None
    if not re.match(r'^https?://', api_url):
        return None
    return f"{api_url}/{quote(user_id)}"