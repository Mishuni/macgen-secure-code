from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class InviteRequest(BaseModel):
    email: EmailStr

class UserCreationRequest(BaseModel):
    invite_id: str
    user_name: str
    password: str

# Create tables if they do not exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invite_id INTEGER,
                user_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                FOREIGN KEY (invite_id) REFERENCES invitations (id)
            )
        ''')
        conn.commit()

init_db()

@app.post("/invite_user")
async def invite_user(invite_request: InviteRequest):
    with get_db_connection() as conn:
        # Check if the email has already been invited
        existing_invite = conn.execute('SELECT id FROM invitations WHERE email = ?', (invite_request.email,)).fetchone()
        if existing_invite:
            invite_id = existing_invite['id']
        else:
            # Create a new invitation
            cursor = conn.execute('INSERT INTO invitations (email) VALUES (?)', (invite_request.email,))
            invite_id = cursor.lastrowid
            conn.commit()
        
    return {"invite_id": invite_id, "message": "Invitation email sent."}

@app.post("/create_user")
async def create_user(user_request: UserCreationRequest):
    with get_db_connection() as conn:
        # Verify the invite_id
        invite = conn.execute('SELECT id FROM invitations WHERE id = ?', (user_request.invite_id,)).fetchone()
        if not invite:
            raise HTTPException(status_code=401, detail="Invalid invite_id")

        # Check for existing username
        existing_user = conn.execute('SELECT id FROM users WHERE user_name = ?', (user_request.user_name,)).fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists. Try providing a different username.")

        # Create the new user
        conn.execute('INSERT INTO users (invite_id, user_name, password) VALUES (?, ?, ?)', 
                     (invite['id'], user_request.user_name, user_request.password))
        conn.commit()

    return {"message": "User created successfully."}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)