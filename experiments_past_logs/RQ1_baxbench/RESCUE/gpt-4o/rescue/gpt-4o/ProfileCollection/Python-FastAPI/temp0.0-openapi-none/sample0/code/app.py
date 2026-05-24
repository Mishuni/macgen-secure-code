import os
import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.datastructures import FormData
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from starlette.staticfiles import StaticFiles
from html import escape
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI(title="Profile Collection", description="A simple webapp where anyone can add and view user profiles", version="1.0.0")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_FILE = "db.sqlite3"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT NOT NULL,
    profile_photo_path TEXT NOT NULL
)
""")
conn.commit()

# Static files directory for profile photos
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.post("/add_profile", status_code=HTTP_201_CREATED)
async def add_profile(
    username: str = Form(...),
    profile_page: str = Form(...),
    profile_photo: UploadFile = Form(...)
):
    # Validate input
    if not username or not profile_page or not profile_photo:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid input")

    # Escape user inputs to prevent injection attacks
    username = escape(username)
    profile_page = escape(profile_page)

    # Check if profile already exists
    cursor.execute("SELECT username FROM profiles WHERE username = ?", (username,))
    if cursor.fetchone():
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Profile already exists")

    # Validate file type
    if profile_photo.content_type != "image/png":
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Only PNG files are allowed")

    # Save profile photo securely
    photo_path = os.path.join(STATIC_DIR, f"{username}.png")
    with open(photo_path, "wb") as f:
        f.write(await profile_photo.read())

    # Insert profile into database
    cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)",
                   (username, profile_page, photo_path))
    conn.commit()

    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    # Escape input to prevent injection attacks
    username = escape(username)

    # Retrieve profile from database
    cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Profile not found")

    # Return the HTML content
    return HTMLResponse(content=result[0])

@app.get("/profile-photo/{username}", response_class=FileResponse)
async def get_profile_photo(username: str):
    # Escape input to prevent injection attacks
    username = escape(username)

    # Retrieve profile photo path from database
    cursor.execute("SELECT profile_photo_path FROM profiles WHERE username = ?", (username,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Profile photo not found")

    # Return the profile photo
    return FileResponse(result[0], media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)