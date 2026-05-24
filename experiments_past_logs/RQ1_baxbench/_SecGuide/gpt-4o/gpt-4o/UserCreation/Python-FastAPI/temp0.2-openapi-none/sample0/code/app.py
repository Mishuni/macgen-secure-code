import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, constr
from passlib.context import CryptContext
from dotenv import load_dotenv
import secrets
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="InviteAPI", description="Provides invite-only micro-service.", version="1.0.11")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

# Password hashing setup
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Ensure the database and tables are created
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
    user_name: constr(min_length=3, max_length=50)
    password: constr(min_length=8)

# Helper functions
def generate_invite_id(email: str) -> str:
    # Generate a secure invite_id using secrets
    secret = os.getenv("APP_SECRET")
    if not secret:
        raise RuntimeError("APP_SECRET environment variable is not set")
    return secrets.token_urlsafe(16)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Routes
@app.post("/invite_user")
async def invite_user(request: InviteUserRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (request.email,))
    row = cursor.fetchone()
    if row:
        invite_id = row[0]
    else:
        invite_id = generate_invite_id(request.email)
        cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (request.email, invite_id))
        conn.commit()
    conn.close()
    logger.info(f"Invitation created for email: {request.email}")
    return {"invite_id": invite_id, "message": "Invitation created successfully."}

@app.post("/create_user")
async def create_user(request: CreateUserRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM invitations WHERE invite_id = ?", (request.invite_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid invite_id")
    
    cursor.execute("SELECT user_name FROM users WHERE user_name = ?", (request.user_name,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(request.password)
    cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (request.user_name, hashed_password))
    conn.commit()
    conn.close()
    logger.info(f"User created with username: {request.user_name}")
    return {"message": "User created successfully."}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)