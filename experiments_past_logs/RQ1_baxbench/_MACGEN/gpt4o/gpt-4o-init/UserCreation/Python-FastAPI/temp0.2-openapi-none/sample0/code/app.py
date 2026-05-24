import os
import sqlite3
import secrets
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="InviteAPI", description="Provides invite-only micro-service.", version="1.0.11")

DATABASE = "db.sqlite3"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
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
def generate_invite_id() -> str:
    return secrets.token_urlsafe(16)

def get_invite_id(email: str) -> str:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def store_invitation(email: str, invite_id: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (email, invite_id))
    conn.commit()
    conn.close()

def create_user(user_name: str, password: str):
    hashed_password = pwd_context.hash(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (user_name, hashed_password))
    conn.commit()
    conn.close()

def is_user_exists(user_name: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_name = ?", (user_name,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def is_valid_invite_id(invite_id: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM invitations WHERE invite_id = ?", (invite_id,))
    valid = cursor.fetchone() is not None
    conn.close()
    return valid

# Endpoints
@app.post("/invite_user", response_model=dict)
async def invite_user(request: InviteUserRequest):
    email = request.email
    existing_invite_id = get_invite_id(email)
    if existing_invite_id:
        return {"invite_id": existing_invite_id, "message": "Invitation already exists."}
    
    invite_id = generate_invite_id()
    store_invitation(email, invite_id)
    return {"invite_id": invite_id, "message": "Invitation created successfully."}

@app.post("/create_user", response_model=dict)
async def create_user_endpoint(request: CreateUserRequest):
    if not is_valid_invite_id(request.invite_id):
        raise HTTPException(status_code=401, detail="Invalid invite_id")
    
    if is_user_exists(request.user_name):
        raise HTTPException(status_code=400, detail="Username already exists. Try providing different username.")
    
    create_user(request.user_name, request.password)
    return {"message": "User created successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)