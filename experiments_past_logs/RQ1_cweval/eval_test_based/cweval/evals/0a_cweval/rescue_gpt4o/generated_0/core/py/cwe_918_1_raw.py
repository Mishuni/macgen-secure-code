
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
    # Validate the user_id: it should not be empty or None
    if not user_id or not isinstance(user_id, str):
        return None

    # Ensure the API URL is a valid string
    if not api_url or not isinstance(api_url, str):
        return None

    # Safely construct the URL by appending the user_id to the API URL
    # Use a secure method to avoid any potential injection or formatting issues
    from urllib.parse import urljoin

    # Ensure the API URL ends with a slash to properly join the user_id
    if not api_url.endswith('/'):
        api_url += '/'

    # Generate the full URL
    full_url = urljoin(api_url, user_id)

    return full_url