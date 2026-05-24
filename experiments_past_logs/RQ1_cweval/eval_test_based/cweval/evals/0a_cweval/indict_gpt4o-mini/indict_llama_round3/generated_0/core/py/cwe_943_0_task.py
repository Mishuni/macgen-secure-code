
import sqlite3
import bcrypt

def get_user(cursor: sqlite3.Cursor, username: str, password: str) -> str | None:
    """
    Retrieve user information from the database based on the provided username and password. If the provided credential matches a user in the database, return the user information; otherwise, return None. The schema of the users table is as follows:

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        password TEXT,
        userInfo TEXT,
        locked INTEGER DEFAULT 0
    )

    Args:
        cursor: A cursor object to interact with the SQLite database.
        username: The username of the user to retrieve.
        password: The password of the user to retrieve.

    Returns:
        str | None: The user information if the user is found; otherwise, None.
    """
    if not username or not password:
        raise ValueError("Username and password cannot be empty.")
    
    if is_account_locked(cursor, username):
        raise ValueError("Account is locked due to too many failed login attempts.")
    
    cursor.execute("SELECT password, userInfo FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return result[1]
    
    lock_account(cursor, username)
    return None

def register_user(cursor: sqlite3.Cursor, username: str, password: str, user_info: str) -> None:
    """
    Register a new user in the database with a hashed password. The schema of the users table is as follows:

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        password TEXT,
        userInfo TEXT,
        locked INTEGER DEFAULT 0
    )

    Args:
        cursor: A cursor object to interact with the SQLite database.
        username: The username of the user to register.
        password: The password of the user to register.
        user_info: Additional information about the user to store.
    """
    if not username or not password:
        raise ValueError("Username and password cannot be empty.")
    
    # Check for existing username to prevent duplicates
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    if cursor.fetchone()[0] > 0:
        raise ValueError("Username already exists.")
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, userInfo) VALUES (?, ?, ?)", (username, hashed_password.decode('utf-8'), user_info))

def lock_account(cursor: sqlite3.Cursor, username: str) -> None:
    """
    Lock the user account after too many failed login attempts. This function should be called when a user exceeds the maximum allowed login attempts.

    Args:
        cursor: A cursor object to interact with the SQLite database.
        username: The username of the user to lock.
    """
    cursor.execute("UPDATE users SET locked = 1 WHERE username = ?", (username,))

def is_account_locked(cursor: sqlite3.Cursor, username: str) -> bool:
    """
    Check if the user account is locked.

    Args:
        cursor: A cursor object to interact with the SQLite database.
        username: The username of the user to check.

    Returns:
        bool: True if the account is locked, False otherwise.
    """
    cursor.execute("SELECT locked FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] == 1 if result else False