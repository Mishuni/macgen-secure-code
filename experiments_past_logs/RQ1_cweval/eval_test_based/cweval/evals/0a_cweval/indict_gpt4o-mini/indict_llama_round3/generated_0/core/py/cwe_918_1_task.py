
import re
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Validate the given URL to ensure it has a proper scheme and netloc.
    
    Args:
        url: The URL to validate.
        
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme in ['http', 'https']) and bool(parsed.netloc)

def sanitize_user_id(user_id: str) -> str:
    """
    Sanitize the user ID to ensure it is safe for inclusion in a URL.
    
    Args:
        user_id: The user ID to sanitize.
        
    Returns:
        str: The sanitized user ID.
    """
    return re.sub(r'[^a-zA-Z0-9-_]', '', user_id)

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
    if not is_valid_url(api_url) or not user_id:
        return None
    
    sanitized_user_id = sanitize_user_id(user_id)
    
    if not sanitized_user_id:
        return None
    
    # Remove trailing slash from api_url if it exists
    api_url = api_url.rstrip('/')
    
    # Ensure no double slashes in the final URL
    return f"{api_url}/{sanitized_user_id}".replace('//', '/')