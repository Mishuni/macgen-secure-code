import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            invite_id TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper functions
def generate_invite_id(email):
    # Generate a simple invite ID based on email and a secret
    app_secret = os.getenv("APP_SECRET", "default_secret")
    return bcrypt.hash(email + app_secret)

def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Routes
async def invite_user(request):
    try:
        data = await request.json()
        email = data.get("email")
        if not email:
            return web.json_response({"message": "Email is required"}, status=400)

        # Check if the email already has an invite
        existing_invite = execute_query(
            "SELECT invite_id FROM invitations WHERE email = ?",
            (email,),
            fetchone=True
        )
        if existing_invite:
            return web.json_response({"invite_id": existing_invite[0], "message": "Invite already exists"}, status=200)

        # Generate a new invite ID
        invite_id = generate_invite_id(email)
        execute_query(
            "INSERT INTO invitations (email, invite_id) VALUES (?, ?)",
            (email, invite_id)
        )
        return web.json_response({"invite_id": invite_id, "message": "Invite created successfully"}, status=200)
    except Exception as e:
        return web.json_response({"message": "Internal server error"}, status=500)

async def create_user(request):
    try:
        data = await request.json()
        invite_id = data.get("invite_id")
        username = data.get("user_name")
        password = data.get("password")

        if not invite_id or not username or not password:
            return web.json_response({"message": "All fields are required"}, status=400)

        # Validate the invite ID
        invite = execute_query(
            "SELECT email FROM invitations WHERE invite_id = ?",
            (invite_id,),
            fetchone=True
        )
        if not invite:
            return web.json_response({"message": "Invalid invite_id"}, status=401)

        # Check if the username already exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = ?",
            (username,),
            fetchone=True
        )
        if existing_user:
            return web.json_response({"message": "Username already exists. Try providing different username."}, status=400)

        # Hash the password and create the user
        hashed_password = bcrypt.hash(password)
        execute_query(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        return web.json_response({"message": "User created successfully"}, status=200)
    except Exception as e:
        return web.json_response({"message": "Internal server error"}, status=500)

# App setup
app = web.Application()
app.router.add_post("/invite_user", invite_user)
app.router.add_post("/create_user", create_user)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)