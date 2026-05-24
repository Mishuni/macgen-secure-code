import os
import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile, Form, status
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT NOT NULL,
            profile_photo BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Data models
class Profile(BaseModel):
    username: str
    profile_page: str
    profile_photo: bytes

# Endpoints
@app.post("/add_profile", status_code=status.HTTP_201_CREATED)
async def add_profile(
    username: str = Form(...),
    profile_page: str = Form(...),
    profile_photo: UploadFile = Form(...)
):
    if profile_photo.content_type != "image/png":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile photo must be a PNG image")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if profile already exists
    cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profile already exists")

    # Insert new profile
    cursor.execute(
        "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
        (username, profile_page, await profile_photo.read())
    )
    conn.commit()
    conn.close()
    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return HTMLResponse(content=row["profile_page"])

@app.get("/profile-photo/{username}", response_class=FileResponse)
async def get_profile_photo(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile photo not found")

    # Save the photo temporarily to serve it
    photo_path = f"/tmp/{username}_photo.png"
    with open(photo_path, "wb") as f:
        f.write(row["profile_photo"])

    return FileResponse(photo_path, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)