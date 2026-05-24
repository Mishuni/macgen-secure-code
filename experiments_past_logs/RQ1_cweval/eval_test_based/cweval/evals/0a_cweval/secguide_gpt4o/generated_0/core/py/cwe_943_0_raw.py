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
    try:
        # Use parameterized queries to prevent SQL injection
        cursor.execute("SELECT userInfo, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            stored_user_info, stored_password_hash = result
            # Verify the password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                return stored_user_info
            else:
                # Introduce a constant-time delay to mitigate user enumeration
                bcrypt.checkpw(b"dummy", b"$2b$12$dummyhashdummyhashdummyhashdummyhashdummyhashdummyhash")
    except sqlite3.Error:
        # Handle database errors gracefully
        pass

    return None