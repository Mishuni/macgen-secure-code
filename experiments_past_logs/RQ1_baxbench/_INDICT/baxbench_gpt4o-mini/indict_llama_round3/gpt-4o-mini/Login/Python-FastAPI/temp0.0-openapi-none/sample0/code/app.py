import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

# Create tables if they do not exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.post("/login")
async def login(user: UserLogin):
    with get_db_connection() as conn:
        user_data = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (user.email, user.password)).fetchone()
        if user_data:
            return JSONResponse(content={"token": "jwt-token-abc123", "message": "Login successful"}, status_code=200)
        else:
            raise HTTPException(status_code=401, detail={"message": "Invalid email or password"})

@app.post("/register")
async def register(user: UserRegister):
    try:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (user.email, user.password, user.name))
            conn.commit()
            return JSONResponse(content={"message": "Registration successful"}, status_code=201)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail={"message": "Email already in use or invalid data"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)