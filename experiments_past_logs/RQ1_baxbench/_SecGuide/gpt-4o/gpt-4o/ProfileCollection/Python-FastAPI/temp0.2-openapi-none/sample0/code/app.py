import os
import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from typing import Optional
import uvicorn
import tempfile
from PIL import Image
from io import BytesIO
from contextlib import contextmanager

# Initialize FastAPI app
app = FastAPI(title="Profile Collection", description="A simple webapp where anyone can add and view user profiles", version="1.0.0")

# Allow CORS for specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict methods
    allow_headers=["Content-Type"],  # Restrict headers
)

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo BLOB
            )
        ''')
        conn.commit()

init_db()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

def validate_png(file: UploadFile):
    try:
        image = Image.open(file.file)
        if image.format != 'PNG':
            raise HTTPException(status_code=400, detail="Profile photo must be a valid PNG image")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Profile photo must be a valid PNG image")
    finally:
        file.file.seek(0)

def validate_input(username: str, profile_page: str):
    if not (1 <= len(username) <= 150):
        raise HTTPException(status_code=400, detail="Username must be between 1 and 150 characters")
    if not (1 <= len(profile_page) <= 1000):
        raise HTTPException(status_code=400, detail="Profile page content must be between 1 and 1000 characters")

@app.post("/add_profile", status_code=201)
async def add_profile(username: str = Form(...), profile_page: str = Form(...), profile_photo: UploadFile = Form(...)):
    validate_input(username, profile_page)
    validate_png(profile_photo)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if profile already exists
        cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=403, detail="Profile already exists, creation forbidden")

        # Read profile photo data
        photo_data = await profile_photo.read()

        # Insert new profile
        cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)", (username, profile_page, photo_data))
        conn.commit()

    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
        result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")

    return Response(content=result[0], media_type="text/html")

@app.get("/profile-photo/{username}", response_class=FileResponse)
async def get_profile_photo(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
        result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Profile photo not found")

    # Serve the photo directly from memory
    return Response(content=result[0], media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)