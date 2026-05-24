import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from dotenv import load_dotenv
from starlette.responses import JSONResponse

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI(title="LoginAPI", description="A simple webapp API for login and registration functionality.", version="1.0.11")

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
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

# Helper functions
def get_user_by_email(email: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password, name FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

def create_user(email: str, hashed_password: str, name: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, hashed_password, name))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already in use")

# Routes
@app.post("/login", summary="User login", description="Authenticate a user with email and password.")
async def login(request: LoginRequest):
    user = get_user_by_email(request.email)
    if not user or not pwd_context.verify(request.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return JSONResponse(content={"token": "jwt-token-abc123", "message": "Login successful"})

@app.post("/register", summary="User registration", description="Register a new user with email, password, and name.")
async def register(request: RegisterRequest):
    hashed_password = pwd_context.hash(request.password)
    create_user(request.email, hashed_password, request.name)
    return JSONResponse(content={"message": "Registration successful"}, status_code=201)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)