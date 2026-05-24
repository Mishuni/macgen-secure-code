from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr, constr
import sqlite3
import os
import uuid
from dotenv import load_dotenv
import bcrypt

load_dotenv()

app = FastAPI()

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv("APP_SECRET")

# Check if APP_SECRET is set
if APP_SECRET is None:
    raise ValueError("APP_SECRET environment variable is not set.")

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT UNIQUE NOT NULL
            )
        ''')
    print("Database initialized.")

init_db()

class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: constr(min_length=36, max_length=36)  # Validate UUID format
    user_name: constr(min_length=3, max_length=30)  # Username validation
    password: constr(min_length=8)  # Password validation

@app.post("/invite_user")
async def invite_user(request: InviteUserRequest):
    email = request.email
    invite_id = str(uuid.uuid4())  # Generate a unique invite_id using UUID

    with get_db_connection() as conn:
        existing_invite = conn.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,)).fetchone()
        if existing_invite:
            invite_id = existing_invite['invite_id']
        else:
            conn.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))

    return {"invite_id": invite_id, "message": "Invitation email prepared."}

@app.post("/create_user")
async def create_user(request: CreateUserRequest):
    invite_id = request.invite_id
    user_name = request.user_name
    password = request.password

    with get_db_connection() as conn:
        invite = conn.execute('SELECT * FROM invitations WHERE invite_id = ?', (invite_id,)).fetchone()
        if not invite:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "User created."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)