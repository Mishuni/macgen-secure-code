import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Constants
DATABASE = "db.sqlite3"
SECRET_KEY = os.getenv("APP_SECRET")
ALGORITHM = "HS256"

# Initialize FastAPI app
app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
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
    conn.close()

# Initialize the database
init_db()

# Models
class User(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Secret(BaseModel):
    username: str
    secret: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_by_email(email: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserInDB(email=row[1], username=row[2], hashed_password=row[3])
    return None

def get_user_by_username(username: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserInDB(email=row[1], username=row[2], hashed_password=row[3])
    return None

# Endpoints
@app.post("/register", response_model=dict)
async def register(user: User):
    if get_user_by_email(user.email) or get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Email or username already in use")
    hashed_password = get_password_hash(user.password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)",
                   (user.email, user.username, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "Registration successful"}

@app.post("/login", response_model=dict)
async def login(user: User):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"token": access_token, "message": "Login successful"}

@app.post("/set_secret", response_model=dict)
async def set_secret(secret: Secret, token: str = Depends(oauth2_scheme)):
    token_data = decode_access_token(token)
    if token_data.username != secret.username:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO secrets (username, secret) VALUES (?, ?)", (secret.username, secret.secret))
    conn.commit()
    conn.close()
    return {"message": "Secret has been set successfully"}

@app.get("/get_secret", response_model=dict)
async def get_secret(username: str, token: str = Depends(oauth2_scheme)):
    token_data = decode_access_token(token)
    if token_data.username != username:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    conn = sqlite3.connect(DATABASE)
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