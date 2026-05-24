import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models for request bodies
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SecretSet(BaseModel):
    username: str
    secret: str

# Create tables if they do not exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS SECRETS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES USERS (username)
            )
        ''')
        conn.commit()

init_db()

@app.post("/register", status_code=201)
async def register_user(user: UserRegister):
    with get_db_connection() as conn:
        try:
            conn.execute('''
                INSERT INTO USERS (email, username, password) 
                VALUES (?, ?, ?)
            ''', (user.email, user.username, user.password))
            conn.commit()
            return {"message": "Registration successful"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already in use or invalid data")

@app.post("/login", status_code=200)
async def login_user(user: UserLogin):
    with get_db_connection() as conn:
        user_data = conn.execute('''
            SELECT * FROM USERS WHERE email = ? AND password = ?
        ''', (user.email, user.password)).fetchone()
        
        if user_data:
            return {"token": "jwt-token-abc123", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/set_secret", status_code=200)
async def set_secret(secret_data: SecretSet):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO SECRETS (username, secret) 
            VALUES (?, ?)
        ''', (secret_data.username, secret_data.secret))
        conn.commit()
        return {"message": "Secret has been set successfully"}

@app.get("/get_secret", status_code=200)
async def get_secret(username: str):
    with get_db_connection() as conn:
        secret_data = conn.execute('''
            SELECT secret FROM SECRETS WHERE username = ?
        ''', (username,)).fetchone()
        
        if secret_data:
            return {"secret": secret_data["secret"]}
        else:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)