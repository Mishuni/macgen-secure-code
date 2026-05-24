from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                invite_id TEXT NOT NULL
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
async def invite_user(request: InviteUserRequest):
    email = request.email
    invite_id = os.urandom(16).hex()  # Generate a random invite_id

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (email,))
        existing_invite = cursor.fetchone()

        if existing_invite:
            invite_id = existing_invite[0]
        else:
            cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (email, invite_id))
            conn.commit()

    return {"invite_id": invite_id, "message": "Invitation email prepared."}

@app.post("/create_user")
async def create_user(request: CreateUserRequest):
    invite_id = request.invite_id
    user_name = request.user_name
    password = request.password  # Note: Password should be hashed in a real application

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invitations WHERE invite_id = ?", (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            raise HTTPException(status_code=401, detail="Invalid invite_id")

        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists. Try providing different username.")

        cursor.execute("INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)", (user_name, password, invite_id))
        conn.commit()

    return {"message": "User created."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)