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
    # Refined regex to ensure username does not start or end with special characters
    if not re.match(r'^(?![.@+-])[a-zA-Z0-9._@+-]{1,148}(?<![.@+-])$', username):
        raise ValueError("Invalid username. It must be 1-150 characters long, contain only letters, numbers, and @/./+/-/_ characters, and cannot start or end with @/./+/-.")

    # Escape the username to prevent HTML injection
    safe_username = html.escape(username)

    return f"Welcome, {safe_username}!"