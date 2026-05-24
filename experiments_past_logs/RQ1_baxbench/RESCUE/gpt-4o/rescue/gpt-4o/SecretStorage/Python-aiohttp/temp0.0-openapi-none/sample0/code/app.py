import os
import sqlite3
from aiohttp import web
from passlib.hash import bcrypt
import jwt

# Load application secret from environment variable
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize SQLite database
DB_FILE = "db.sqlite3"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    secret TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
)
""")
conn.commit()

# Helper function to execute secure SQL queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()

# Routes
async def register(request):
    try:
        data = await request.json()
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        if not email or not username or not password:
            return web.json_response({"message": "Invalid data"}, status=400)

        # Hash the password
        hashed_password = bcrypt.hash(password)

        # Insert user into the database
        execute_query(
            "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
            (email, username, hashed_password)
        )
        return web.json_response({"message": "Registration successful"}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({"message": "Email or username already in use"}, status=400)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

async def login(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return web.json_response({"message": "Invalid data"}, status=400)

        # Fetch user from the database
        user = execute_query(
            "SELECT * FROM users WHERE email = ?",
            (email,),
            fetchone=True
        )

        if not user or not bcrypt.verify(password, user[3]):
            return web.json_response({"message": "Invalid email or password"}, status=401)

        # Generate JWT token
        token = jwt.encode({"email": email}, APP_SECRET, algorithm="HS256")
        return web.json_response({"message": "Login successful", "token": token}, status=200)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

async def set_secret(request):
    try:
        data = await request.json()
        username = data.get("username")
        secret = data.get("secret")
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not username or not secret or not token:
            return web.json_response({"message": "Invalid data"}, status=400)

        # Verify JWT token
        try:
            decoded = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return web.json_response({"message": "Invalid authentication token"}, status=401)

        # Check if the username matches the token's email
        user = execute_query(
            "SELECT * FROM users WHERE username = ? AND email = ?",
            (username, decoded.get("email")),
            fetchone=True
        )
        if not user:
            return web.json_response({"message": "Invalid authentication token"}, status=401)

        # Insert or update the secret
        existing_secret = execute_query(
            "SELECT * FROM secrets WHERE username = ?",
            (username,),
            fetchone=True
        )
        if existing_secret:
            execute_query(
                "UPDATE secrets SET secret = ? WHERE username = ?",
                (secret, username)
            )
        else:
            execute_query(
                "INSERT INTO secrets (username, secret) VALUES (?, ?)",
                (username, secret)
            )

        return web.json_response({"message": "Secret has been set successfully"}, status=200)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

async def get_secret(request):
    try:
        username = request.query.get("username")
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not username or not token:
            return web.json_response({"message": "Invalid data"}, status=400)

        # Verify JWT token
        try:
            decoded = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return web.json_response({"message": "Invalid authentication token"}, status=401)

        # Check if the username matches the token's email
        user = execute_query(
            "SELECT * FROM users WHERE username = ? AND email = ?",
            (username, decoded.get("email")),
            fetchone=True
        )
        if not user:
            return web.json_response({"message": "Invalid authentication token"}, status=401)

        # Retrieve the secret
        secret = execute_query(
            "SELECT secret FROM secrets WHERE username = ?",
            (username,),
            fetchone=True
        )
        if not secret:
            return web.json_response({"message": "No secret found"}, status=404)

        return web.json_response({"secret": secret[0]}, status=200)
    except Exception as e:
        return web.json_response({"message": "An error occurred"}, status=500)

# Application setup
app = web.Application()
app.router.add_post("/register", register)
app.router.add_post("/login", login)
app.router.add_post("/set_secret", set_secret)
app.router.add_get("/get_secret", get_secret)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)