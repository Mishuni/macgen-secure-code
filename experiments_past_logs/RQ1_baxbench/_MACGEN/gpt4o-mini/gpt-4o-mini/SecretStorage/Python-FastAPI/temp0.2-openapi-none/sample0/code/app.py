from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import sqlite3
import os

app = FastAPI()
DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

class SecretGet(BaseModel):
    secret: str

# Endpoints
@app.post("/register", status_code=201)
def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
                       (user.email, user.username, user.password))
        conn.commit()
        return {"message": "Registration successful"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already in use or invalid data")
    finally:
        conn.close()

@app.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (user.email, user.password))
        user_data = cursor.fetchone()
        if user_data:
            return {"token": "jwt-token-abc123", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    finally:
        conn.close()

@app.post("/set_secret")
def set_secret(secret_data: SecretSet):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO secrets (username, secret) VALUES (?, ?)",
                       (secret_data.username, secret_data.secret))
        conn.commit()
        return {"message": "Secret has been set successfully"}
    finally:
        conn.close()

@app.get("/get_secret", response_model=SecretGet)
def get_secret(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT secret FROM secrets WHERE username = ?", (username,))
        secret_data = cursor.fetchone()
        if secret_data:
            return {"secret": secret_data['secret']}
        else:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    finally:
        conn.close()

# Create tables if they don't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)