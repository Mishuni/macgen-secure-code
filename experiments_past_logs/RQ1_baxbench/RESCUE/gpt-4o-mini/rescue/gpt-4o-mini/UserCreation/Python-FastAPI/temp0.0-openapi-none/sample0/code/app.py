import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# FastAPI app
app = FastAPI()

# Pydantic models
class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

class InviteResponse(BaseModel):
    invite_id: str
    message: str

class UserResponse(BaseModel):
    message: str

# Create tables if they do not exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                invite_id TEXT NOT NULL,
                FOREIGN KEY (invite_id) REFERENCES invitations (invite_id)
            )
        ''')
        conn.commit()

init_db()

@app.post("/invite_user", response_model=InviteResponse)
def invite_user(request: InviteUserRequest):
    with get_db_connection() as conn:
        # Check if the email already has an invitation
        existing_invite = conn.execute('SELECT invite_id FROM invitations WHERE email = ?', (request.email,)).fetchone()
        if existing_invite:
            return InviteResponse(invite_id=existing_invite['invite_id'], message="Invitation already exists.")

        # Create a new invitation
        invite_id = os.urandom(16).hex()  # Generate a random invite_id
        conn.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (request.email, invite_id))
        conn.commit()
        return InviteResponse(invite_id=invite_id, message="Invitation created successfully.")

@app.post("/create_user", response_model=UserResponse)
def create_user(request: CreateUserRequest):
    with get_db_connection() as conn:
        # Check if the invite_id is valid
        invite = conn.execute('SELECT * FROM invitations WHERE invite_id = ?', (request.invite_id,)).fetchone()
        if not invite:
            raise HTTPException(status_code=401, detail="Invalid invite_id")

        # Check if the username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE user_name = ?', (request.user_name,)).fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists. Try providing a different username.")

        # Create the new user
        conn.execute('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', (request.user_name, request.password, request.invite_id))
        conn.commit()
        return UserResponse(message="User created successfully.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)