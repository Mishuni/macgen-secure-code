import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, constr
from passlib.context import CryptContext
from jose import jwt
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
import logging

load_dotenv()

# Load application secret from environment variable
APP_SECRET = os.getenv("APP_SECRET")
if not APP_SECRET:
    raise RuntimeError("APP_SECRET environment variable is not set")

# Load database path from environment variable
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

# Initialize FastAPI app
app = FastAPI(title="LoginAPI", version="1.0.11")

# Add HTTPS redirect middleware
app.add_middleware(HTTPSRedirectMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: constr(min_length=1, max_length=50)

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, APP_SECRET, algorithm="HS256")

# Dependency
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Routes
@app.post("/login", tags=["Authentication"])
async def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()
    if not result or not verify_password(user.password, result[1]):
        logger.warning(f"Failed login attempt for email: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = result[0]
    token = create_access_token({"sub": user.email, "id": user_id})
    return JSONResponse(content={"token": token, "message": "Login successful"})

@app.post("/register", tags=["Authentication"])
async def register(user: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        hashed_password = get_password_hash(user.password)
        cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                       (user.email, hashed_password, user.name))
        db.commit()
    except sqlite3.IntegrityError as e:
        logger.error(f"Registration failed for email: {user.email}, error: {str(e)}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return JSONResponse(content={"message": "Registration successful"}, status_code=201)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)