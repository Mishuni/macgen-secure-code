import sqlite3
import bcrypt


def get_user(cursor: sqlite3.Cursor, username: str, password: str) -> str | None:
    query = "SELECT password, userInfo FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return result[1]
    
    return None