import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv("APP_SECRET")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class User(BaseModel):
    email: EmailStr
    password: str
    name: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

class RegistrationResponse(BaseModel):
    message: str

# Create tables if they do not exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT
            )
        ''')
        conn.commit()

init_db()

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (request.email, request.password)).fetchone()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"token": "jwt-token-abc123", "message": "Login successful"}

@app.post("/register", response_model=RegistrationResponse)
async def register(user: User):
    try:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (user.email, user.password, user.name))
            conn.commit()
            return {"message": "Registration successful"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already in use or invalid data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)