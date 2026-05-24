import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

app = FastAPI(title="InviteAPI", description="Provides invite-only micro-service.", version="1.0.11")

DATABASE = "db.sqlite3"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

@app.post("/invite_user", response_model=dict)
async def invite_user(request: InviteUserRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (request.email,))
    row = cursor.fetchone()
    
    if row:
        invite_id = row[0]
    else:
        invite_id = os.urandom(16).hex()
        cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (request.email, invite_id))
        conn.commit()
    
    conn.close()
    return {"invite_id": invite_id, "message": "Invitation created successfully."}

@app.post("/create_user", response_model=dict)
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
        raise HTTPException(status_code=400, detail="Username already exists. Try providing different username.")
    
    hashed_password = pwd_context.hash(request.password)
    cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (request.user_name, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)