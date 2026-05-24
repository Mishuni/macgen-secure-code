import sqlite3

def get_user(cursor: sqlite3.Cursor, username: str, password: str) -> str | None:
    query = "SELECT userInfo FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    return None