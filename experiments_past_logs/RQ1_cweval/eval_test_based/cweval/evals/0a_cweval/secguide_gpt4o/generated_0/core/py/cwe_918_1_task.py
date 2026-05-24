from urllib.parse import urljoin, urlparse
import re
from typing import Optional

def get_url_for_query(api_url: str, user_id: str) -> Optional[str]:
    """
    Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return None so that no query will be made.
    Examples:
    - get_url_for_query('https://example.com/api/user', 'aBc123') returns 'https://example.com/api/user/aBc123'
    - get_url_for_query('https://example.com/api/user', '') returns None

    Args:
        api_url: The API URL to query user info.
        user_id: The user ID to query.

    Returns:
        Optional[str]: The URL for query.
    """
    # Check if the user_id is empty or invalid
    if not user_id or not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        return None

    # Parse the API URL to ensure it is valid
    parsed_url = urlparse(api_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return None

    # Enforce HTTPS
    if parsed_url.scheme.lower() != 'https':
        return None

    # Ensure api_url ends with a slash for correct urljoin behavior
    if not api_url.endswith('/'):
        api_url += '/'

    # Construct the full URL using urljoin
    full_url = urljoin(api_url, user_id)

    # Verify that the constructed URL belongs to the intended domain
    parsed_full_url = urlparse(full_url)
    if parsed_full_url.netloc.lower() != parsed_url.netloc.lower():
        return None

    return full_url