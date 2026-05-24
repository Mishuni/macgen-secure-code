import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
APP_SECRET = os.getenv("APP_SECRET")
DATABASE = "db.sqlite3"

# Initialize FastAPI app
app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class User(BaseModel):
    email: EmailStr
    username: str
    password: str

class Secret(BaseModel):
    username: str
    secret: str

class TokenData(BaseModel):
    username: str

# Create tables
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
init_db()

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT token
def create_access_token(data: dict):
    return jwt.encode(data, APP_SECRET, algorithm="HS256")

# User registration
@app.post("/register")
async def register(user: User):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)',
                         (user.email, user.username, hash_password(user.password)))
            return {"message": "Registration successful"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already in use or invalid data")

# User login
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (form_data.username,)).fetchone()
        if not user or not verify_password(form_data.password, user['hashed_password']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_access_token(data={"sub": user['username']})
        return {"token": token, "message": "Login successful"}

# Set secret
@app.post("/set_secret")
async def set_secret(secret: Secret, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        if username != secret.username:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    with get_db_connection() as conn:
        conn.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (secret.username, secret.secret))
        return {"message": "Secret has been set successfully"}

# Get secret
@app.get("/get_secret")
async def get_secret(username: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        if payload.get("sub") != username:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    with get_db_connection() as conn:
        secret = conn.execute('SELECT secret FROM secrets WHERE username = ?', (username,)).fetchone()
        if secret:
            return {"secret": secret['secret']}
        raise HTTPException(status_code=404, detail="Secret not found")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)