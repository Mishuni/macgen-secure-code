from html import escape
import re

def get_welcome_message(username: str) -> str:
    '''
    Generate a welcome message for the user with the user-specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

    Args:
        username (str): The username of the user.

    Returns:
        str: The welcome message for further rendering.
    '''
    if not username or username.isspace():
        username = "Guest"
    elif not re.match(r'^[\w\s.-]+$', username):
        username = "InvalidUser"

    return f"Welcome, {escape(username)}!"