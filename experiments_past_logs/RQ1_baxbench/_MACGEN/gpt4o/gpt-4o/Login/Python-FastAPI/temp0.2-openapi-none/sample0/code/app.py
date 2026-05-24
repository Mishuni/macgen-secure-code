import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LoginAPI", description="A simple webapp API for login and registration functionality.", version="1.0.11")

DATABASE = "db.sqlite3"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_user_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

create_user_table()

@app.post("/register", status_code=HTTP_201_CREATED)
async def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    try:
        hashed_password = pwd_context.hash(user.password)
        cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (user.email, hashed_password, user.name))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already in use or invalid data")
    finally:
        conn.close()
    return JSONResponse(status_code=HTTP_201_CREATED, content={"message": "Registration successful"})

@app.post("/login", status_code=HTTP_200_OK)
async def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = "jwt-token-abc123"  # Placeholder token
    return JSONResponse(status_code=HTTP_200_OK, content={"token": token, "message": "Login successful"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)