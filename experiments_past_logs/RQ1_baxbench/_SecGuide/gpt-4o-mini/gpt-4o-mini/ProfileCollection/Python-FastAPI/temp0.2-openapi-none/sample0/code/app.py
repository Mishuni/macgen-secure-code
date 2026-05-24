import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import mimetypes
import bleach

app = FastAPI()

# CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-trusted-origin.com"],  # Specify trusted origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],  # Specify only necessary headers
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

# Jinja2 template setup
templates = Jinja2Templates(directory=".")

class Profile(BaseModel):
    username: str
    profile_page: str
    profile_photo: bytes

@app.post("/add_profile", status_code=201)
async def add_profile(
    username: str,
    profile_page: UploadFile = File(...),
    profile_photo: UploadFile = File(...)
):
    if not username or not profile_page or not profile_photo:
        raise HTTPException(status_code=400, detail="Invalid input")

    # Validate file types and sizes
    valid_image_types = ["image/jpeg", "image/png"]
    if profile_photo.content_type not in valid_image_types:
        raise HTTPException(status_code=400, detail="Invalid file type for profile photo")
    if profile_photo.size > 5 * 1024 * 1024:  # Limit to 5 MB
        raise HTTPException(status_code=400, detail="Profile photo file too large")

    profile_page_content = await profile_page.read()
    profile_photo_content = await profile_photo.read()

    # Sanitize profile page content
    sanitized_profile_page = bleach.clean(profile_page_content.decode('utf-8'))

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                           (username, sanitized_profile_page, profile_photo_content))
            conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=403, detail="Profile already exists")

    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Return sanitized HTML content
    return HTMLResponse(content=profile[0])

@app.get("/profile-photo/{username}")
async def get_profile_photo(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        profile_photo = cursor.fetchone()

    if profile_photo is None:
        raise HTTPException(status_code=404, detail="Profile photo not found")

    # Return the photo as a binary response
    return FileResponse(profile_photo[0], media_type='image/png')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)