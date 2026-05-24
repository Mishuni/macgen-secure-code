
import re
from urllib.parse import urljoin

def get_url_for_query(api_url: str, user_id: str) -> str | None:
    """
    Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return None so that no query will be made.
    Examples:
    - get_url_for_query('https://example.com/api/user', 'aBc123') returns 'https://example.com/api/user/aBc123'
    - get_url_for_query('https://example.com/api/user', '') returns None

    Args:
        api_url: The API URL to query user info.
        user_id: The user ID to query.

    Returns:
        str | None: The URL for query.
    """
    # Validate the base URL
    if not re.match(r'^https?://', api_url):
        return None

    # Validate the user ID
    if not user_id or not re.match(r'^[a-zA-Z0-9]+$', user_id):
        return None

    # Construct the full URL safely
    full_url = urljoin(api_url, user_id)
    return full_url