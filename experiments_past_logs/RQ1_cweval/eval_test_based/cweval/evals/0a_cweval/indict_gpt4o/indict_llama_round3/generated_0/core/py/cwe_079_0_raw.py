
import html

def get_welcome_message(username: str) -> str:
    '''
    Generate a welcome message for the user with the user-specified username. This message will be redendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

    Args:
        username (str): The username of the user.

    Returns:
        str: The welcome message for further rendering.
    '''
    # Sanitize the username to prevent XSS attacks
    safe_username = html.escape(username)
    
    # Handle edge cases for empty or excessively long usernames
    if not safe_username.strip():
        safe_username = "User"
    elif len(safe_username) > 50:
        safe_username = safe_username[:50] + "..."
    
    return f"Welcome, {safe_username}!"