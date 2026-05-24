import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr, validator
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv("APP_SECRET")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Models
class User(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=30)
    password: constr(min_length=8)

class Secret(BaseModel):
    username: constr(min_length=3, max_length=30)
    secret: constr(min_length=1)  # Ensure secret is not empty

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# Create tables
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    print("Database initialized.")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/register", response_model=dict)
def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
                         (user.email, user.username, hashed_password))
            return {"message": "Registration successful"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already in use or invalid data")

@app.post("/login", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (form_data.username,)).fetchone()
        if user and pwd_context.verify(form_data.password, user['password']):
            # Generate a JWT token dynamically (placeholder for actual implementation)
            return {"token": "jwt-token-abc123", "message": "Login successful"}
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/set_secret", response_model=dict)
def set_secret(secret: Secret, token: str = Depends(oauth2_scheme)):
    # Token validation should be implemented here
    with get_db_connection() as conn:
        user = conn.execute('SELECT id FROM users WHERE username = ?', (secret.username,)).fetchone()
        if user:
            conn.execute('INSERT INTO secrets (user_id, secret) VALUES (?, ?)',
                         (user['id'], secret.secret))
            return {"message": "Secret has been set successfully"}
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/get_secret", response_model=dict)
def get_secret(username: str, token: str = Depends(oauth2_scheme)):
    # Token validation should be implemented here
    with get_db_connection() as conn:
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            secret = conn.execute('SELECT secret FROM secrets WHERE user_id = ?', (user['id'],)).fetchone()
            if secret:
                return {"secret": secret['secret']}
        raise HTTPException(status_code=404, detail="Secret not found or user not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)