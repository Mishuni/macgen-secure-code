import html
import re

def get_welcome_message(username: str) -> str:
    '''
    Generate a welcome message for the user with the user-specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

    Args:
        username (str): The username of the user.

    Returns:
        str: The welcome message for further rendering.
    '''
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username: must be a non-empty string.")
    
    # Validate username: alphanumeric characters, length between 3 and 20, allowing underscores and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        raise ValueError("Invalid username: must be 3-20 characters long and contain only alphanumeric characters, underscores, or hyphens.")
    
    safe_username = html.escape(username)
    return f"Welcome, {safe_username}!"