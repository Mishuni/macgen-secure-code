import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "defaultsecret")

# Initialize FastAPI app
app = FastAPI(title="LoginAPI", version="1.0.11", description="A simple webapp API for login and registration functionality.")

# Database setup
DATABASE = "db.sqlite3"

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
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

# Dependency to get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Routes
@app.post("/login", response_model=dict)
def login(request: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (request.email, request.password))
    user = cursor.fetchone()
    if user:
        return JSONResponse(status_code=HTTP_200_OK, content={"token": "jwt-token-abc123", "message": "Login successful"})
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

@app.post("/register", response_model=dict)
def register(request: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (request.email, request.password, request.name))
        db.commit()
        return JSONResponse(status_code=HTTP_201_CREATED, content={"message": "Registration successful"})
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already in use or invalid data")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)