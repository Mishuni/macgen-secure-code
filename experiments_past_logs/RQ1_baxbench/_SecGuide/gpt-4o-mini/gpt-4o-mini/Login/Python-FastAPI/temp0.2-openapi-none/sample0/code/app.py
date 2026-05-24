import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr, validator
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "a_very_complex_default_secret_123!")  # More complex default

# Database setup
DATABASE = "db.sqlite3"

# FastAPI app initialization
app = FastAPI()

# CORS middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-trusted-origin.com"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTPS redirect middleware
app.add_middleware(HTTPSRedirectMiddleware)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email: str, password: str, name: str):
    hashed_password = pwd_context.hash(password)
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, hashed_password, name))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already in use")
    finally:
        conn.close()

def get_user(email: str):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

# Models
class User(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # Enforce minimum password length
    name: str

    @validator('password')
    def password_complexity(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

class Token(BaseModel):
    token: str
    message: str

# Create the users table if it doesn't exist
def init_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/register", response_model=Token)
def register(user: User):
    create_user(user.email, user.password, user.name)
    return {"message": "Registration successful"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")  # More generic error message
    
    # Create JWT token
    token_data = {
        "sub": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_data, APP_SECRET, algorithm="HS256")
    
    return {"token": token, "message": "Login successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)