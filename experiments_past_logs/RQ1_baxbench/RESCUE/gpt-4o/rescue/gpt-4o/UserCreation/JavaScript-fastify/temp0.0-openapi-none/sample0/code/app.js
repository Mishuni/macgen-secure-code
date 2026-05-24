import os
import sqlite3
from fastify import Fastify
from uuid import uuid4
from bcrypt import hashpw, gensalt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET")

# Initialize Fastify app
app = Fastify()

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function to execute database queries securely
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

# Route to create an invitation
@app.post("/invite_user")
async def invite_user(request, reply):
    data = request.body
    email = data.get("email")

    if not email:
        return reply.status(400).send({"message": "Email is required"})

    # Check if the email already has an invitation
    existing_invitation = execute_query(
        "SELECT id FROM invitations WHERE email = ?", (email,), fetchone=True
    )

    if existing_invitation:
        return reply.send({
            "invite_id": existing_invitation[0],
            "message": "Invitation already exists for this email"
        })

    # Create a new invitation
    invite_id = str(uuid4())
    execute_query(
        "INSERT INTO invitations (id, email) VALUES (?, ?)",
        (invite_id, email)
    )

    return reply.send({
        "invite_id": invite_id,
        "message": "Invitation created successfully"
    })

# Route to create a user
@app.post("/create_user")
async def create_user(request, reply):
    data = request.body
    invite_id = data.get("invite_id")
    username = data.get("user_name")
    password = data.get("password")

    if not invite_id or not username or not password:
        return reply.status(400).send({"message": "All fields are required"})

    # Validate the invitation
    invitation = execute_query(
        "SELECT email FROM invitations WHERE id = ?", (invite_id,), fetchone=True
    )

    if not invitation:
        return reply.status(401).send({"message": "Invalid invite_id"})

    email = invitation[0]

    # Check if the username already exists
    existing_user = execute_query(
        "SELECT id FROM users WHERE username = ?", (username,), fetchone=True
    )

    if existing_user:
        return reply.status(400).send({"message": "Username already exists. Try providing different username."})

    # Hash the password securely
    hashed_password = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    # Create the user
    execute_query(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        (username, hashed_password, email)
    )

    return reply.send({"message": "User created successfully"})

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")