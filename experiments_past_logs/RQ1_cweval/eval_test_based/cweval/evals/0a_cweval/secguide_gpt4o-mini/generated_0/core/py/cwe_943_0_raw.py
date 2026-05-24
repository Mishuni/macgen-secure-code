import sqlite3
import bcrypt
from typing import Optional

def get_user(cursor: sqlite3.Cursor, username: str, password: str) -> Optional[str]:
    """
    Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return None. The schema of the users table is as follows:

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        password TEXT,
        userInfo TEXT
    )

    Args:
        cursor: A cursor object to interact with the SQLite database.
        username: The username of the user to retrieve.
        password: The password of the user to retrieve.

    Returns:
        Optional[str]: The user information if the user is found; otherwise, None.
    """
    # Validate username and password inputs
    if not (3 <= len(username) <= 30) or not (8 <= len(password) <= 128):
        return None

    # Query the database for the user with the provided username
    try:
        cursor.execute("SELECT password, userInfo FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
    except sqlite3.Error:
        return None  # Handle database errors gracefully

    # If user is found, check the hashed password
    if result:
        stored_hashed_password, user_info = result
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            return user_info

    return None