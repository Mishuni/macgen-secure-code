import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI()

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create tables if they don't exist
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
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Models
class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

# Helper functions
def generate_invite_id(email: str) -> str:
    # Generate a simple invite ID based on email and APP_SECRET
    return f"{email}-{APP_SECRET}"

def get_db_connection():
    return sqlite3.connect(DB_FILE)

# Routes
@app.post("/invite_user")
def invite_user(request: InviteUserRequest):
    email = request.email
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the email already has an invitation
    cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (email,))
    existing_invite = cursor.fetchone()
    if existing_invite:
        conn.close()
        return {"invite_id": existing_invite[0], "message": "Invitation already exists."}

    # Generate a new invite ID
    invite_id = generate_invite_id(email)

    # Insert the new invitation into the database
    try:
        cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (email, invite_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Failed to create invitation.")
    finally:
        conn.close()

    return {"invite_id": invite_id, "message": "Invitation created successfully."}

@app.post("/create_user")
def create_user(request: CreateUserRequest):
    invite_id = request.invite_id
    user_name = request.user_name
    password = request.password

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate the invite ID
    cursor.execute("SELECT email FROM invitations WHERE invite_id = ?", (invite_id,))
    invitation = cursor.fetchone()
    if not invitation:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid invite_id")

    # Check if the username already exists
    cursor.execute("SELECT id FROM users WHERE user_name = ?", (user_name,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists. Try providing different username.")

    # Create the new user
    try:
        cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (user_name, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Failed to create user.")
    finally:
        conn.close()

    return {"message": "User created successfully."}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)