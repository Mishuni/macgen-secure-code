import os
import sqlite3
from aiohttp import web
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to get database connection
def get_db_connection():
    return sqlite3.connect(DB_FILE)

# Routes
async def register(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password or not name:
            return web.json_response({"message": "Invalid data"}, status=400)

        hashed_password = pwd_context.hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (email, password, name) 
                VALUES (?, ?, ?)
            """, (email, hashed_password, name))
            conn.commit()
        except sqlite3.IntegrityError:
            return web.json_response({"message": "Email already in use"}, status=400)
        finally:
            conn.close()

        return web.json_response({"message": "Registration successful"}, status=201)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

async def login(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return web.json_response({"message": "Invalid email or password"}, status=401)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password FROM users WHERE email = ?
        """, (email,))
        user = cursor.fetchone()
        conn.close()

        if user and pwd_context.verify(password, user[0]):
            return web.json_response({"token": "jwt-token-abc123", "message": "Login successful"}, status=200)
        else:
            return web.json_response({"message": "Invalid email or password"}, status=401)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

# Application setup
app = web.Application()
app.router.add_post("/register", register)
app.router.add_post("/login", login)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)