import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DATABASE = 'db.sqlite3'

# Database setup
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        conn.commit()

init_db()

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

class SecretResponse(BaseModel):
    secret: str

@app.post("/register", response_model=dict)
async def register(user: UserRegister):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
                           (user.email, user.username, user.password))
            conn.commit()
        return JSONResponse(status_code=201, content={"message": "Registration successful"})
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already in use or invalid data")

@app.post("/login", response_model=dict)
async def login(user: UserLogin):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (user.email, user.password))
        result = cursor.fetchone()
        if result:
            return {"token": "jwt-token-abc123", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/set_secret", response_model=dict)
async def set_secret(secret_data: SecretSet):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO secrets (username, secret) VALUES (?, ?)",
                       (secret_data.username, secret_data.secret))
        conn.commit()
    return {"message": "Secret has been set successfully"}

@app.get("/get_secret", response_model=SecretResponse)
async def get_secret(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT secret FROM secrets WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return SecretResponse(secret=result[0])
        else:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)