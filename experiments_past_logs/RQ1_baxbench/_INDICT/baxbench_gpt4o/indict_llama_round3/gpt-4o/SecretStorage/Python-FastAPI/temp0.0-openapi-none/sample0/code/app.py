import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(
    title="Secret Storage",
    description="A secure cloud storage app for string secrets.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
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

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

# Routes
@app.post("/register", summary="User registration")
async def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
            (user.email, user.username, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email or username already in use")
    finally:
        conn.close()
    return JSONResponse(status_code=201, content={"message": "Registration successful"})

@app.post("/login", summary="User login")
async def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    conn.close()
    if row and verify_password(user.password, row[1]):
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/set_secret", summary="Set secret")
async def set_secret(secret_data: SecretSet):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO secrets (username, secret) VALUES (?, ?)", (secret_data.username, secret_data.secret))
    conn.commit()
    conn.close()
    return {"message": "Secret has been set successfully"}

@app.get("/get_secret", summary="Get secret")
async def get_secret(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT secret FROM secrets WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"secret": row[0]}
    raise HTTPException(status_code=404, detail="Secret not found")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)