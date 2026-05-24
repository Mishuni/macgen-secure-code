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
    parsed_url = urlparse(api_url)
    
    if not parsed_url.scheme or not parsed_url.netloc or not user_id:
        return None
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):  # Updated regex to allow underscores and dashes
        return None
    
    # No need for sanitization if we validate correctly
    return urljoin(api_url.rstrip('/') + '/', user_id)  # Ensures proper URL construction