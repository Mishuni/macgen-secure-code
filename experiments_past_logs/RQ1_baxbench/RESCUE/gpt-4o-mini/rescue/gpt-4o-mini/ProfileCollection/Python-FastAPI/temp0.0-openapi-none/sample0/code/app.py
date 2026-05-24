import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from html import escape

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory=".")

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

@app.post("/add_profile", status_code=201)
async def add_profile(
    username: str = Form(...),
    profile_page: UploadFile = File(...),
    profile_photo: UploadFile = File(...)
):
    # Escape username to prevent XSS
    username = escape(username)

    # Check if the profile already exists
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=403, detail="Profile already exists, creation forbidden")

        # Read and sanitize profile page content
        profile_page_content = await profile_page.read()
        profile_page_content = escape(profile_page_content.decode('utf-8'))

        # Read profile photo
        profile_photo_content = await profile_photo.read()

        # Insert new profile into the database
        cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
                       (username, profile_page_content, profile_photo_content))
        conn.commit()

    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    username = escape(username)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
        profile = cursor.fetchone()
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        return HTMLResponse(content=profile[0])

@app.get("/profile-photo/{username}")
async def get_profile_photo(username: str):
    username = escape(username)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
        profile_photo = cursor.fetchone()
        if profile_photo is None:
            raise HTTPException(status_code=404, detail="Profile photo not found")

        return FileResponse(profile_photo[0], media_type='image/png')

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)