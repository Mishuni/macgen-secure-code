from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sqlite3
import os
import uuid

app = FastAPI()
DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                invite_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

class InviteUserRequest(BaseModel):
    email: EmailStr

class CreateUserRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

@app.post("/invite_user")
def invite_user(request: InviteUserRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (request.email,))
        invitation = cursor.fetchone()
        
        if invitation:
            invite_id = invitation[0]
        else:
            invite_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", (invite_id, request.email))
        
        conn.commit()
        return {"invite_id": invite_id, "message": "Invitation email sent."}

@app.post("/create_user")
def create_user(request: CreateUserRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM invitations WHERE invite_id = ?", (request.invite_id,))
        invitation = cursor.fetchone()
        
        if not invitation:
            raise HTTPException(status_code=401, detail="Invalid invite_id")
        
        cursor.execute("SELECT username FROM users WHERE username = ?", (request.user_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists. Try providing a different username.")
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (request.user_name, request.password))
        conn.commit()
        return {"message": "User created."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)