import os
import sqlite3
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

# Helper functions
def create_invite(email: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        return row["invite_id"]
    
    invite_id = os.urandom(16).hex()
    cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (email, invite_id))
    conn.commit()
    conn.close()
    return invite_id

def create_user(invite_id: str, user_name: str, password: str) -> Optional[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM invitations WHERE invite_id = ?", (invite_id,))
    row = cursor.fetchone()
    if not row:
        return None
    
    cursor.execute("SELECT user_name FROM users WHERE user_name = ?", (user_name,))
    if cursor.fetchone():
        return "Username already exists. Try providing different username."
    
    hashed_password = pwd_context.hash(password)
    cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (user_name, hashed_password))
    conn.commit()
    conn.close()
    return "User created successfully."

# Endpoints
@app.post("/invite_user", status_code=status.HTTP_200_OK)
async def invite_user(request: InviteUserRequest):
    invite_id = create_invite(request.email)
    return {"invite_id": invite_id, "message": "Invitation created successfully."}

@app.post("/create_user", status_code=status.HTTP_200_OK)
async def create_user_endpoint(request: CreateUserRequest):
    result = create_user(request.invite_id, request.user_name, request.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid invite_id")
    elif result.startswith("Username already exists"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return {"message": result}

# Initialize database
def init_db():
    conn = get_db_connection()
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
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Run database initialization
init_db()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)