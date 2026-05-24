import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI(title="Secret Storage", description="A secure cloud storage app for string secrets.", version="1.0.0")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        """)
        conn.commit()

init_db()

# Models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SetSecretRequest(BaseModel):
    username: str
    secret: str

# Helper functions
def get_db_connection():
    return sqlite3.connect(DB_NAME)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Routes
@app.post("/register", status_code=201)
async def register_user(request: RegisterRequest):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            hashed_password = hash_password(request.password)
            cursor.execute("""
                INSERT INTO users (email, username, password) 
                VALUES (?, ?, ?)
            """, (request.email, request.username, hashed_password))
            conn.commit()
        return {"message": "Registration successful"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email or username already in use")

@app.post("/login")
async def login_user(request: LoginRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password FROM users WHERE email = ?
        """, (request.email,))
        user = cursor.fetchone()
        if user and verify_password(request.password, user[0]):
            return {"message": "Login successful", "token": APP_SECRET}
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/set_secret")
async def set_secret(request: SetSecretRequest, token: str = Depends(lambda req: req.headers.get("Authorization", "").replace("Bearer ", ""))):
    if token != APP_SECRET:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username FROM users WHERE username = ?
        """, (request.username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid username")
        cursor.execute("""
            INSERT INTO secrets (username, secret) 
            VALUES (?, ?)
        """, (request.username, request.secret))
        conn.commit()
    return {"message": "Secret has been set successfully"}

@app.get("/get_secret")
async def get_secret(username: str, token: str = Depends(lambda req: req.headers.get("Authorization", "").replace("Bearer ", ""))):
    if token != APP_SECRET:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT secret FROM secrets WHERE username = ?
        """, (username,))
        secret = cursor.fetchone()
        if not secret:
            raise HTTPException(status_code=400, detail="No secret found for the given username")
        return {"secret": secret[0]}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)