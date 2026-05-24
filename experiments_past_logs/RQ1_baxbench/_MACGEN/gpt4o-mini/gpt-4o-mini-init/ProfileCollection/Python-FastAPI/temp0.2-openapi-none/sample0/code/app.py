from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, constr
import sqlite3
import os

app = FastAPI()

DATABASE = "db.sqlite3"

class UserProfile(BaseModel):
    username: constr(regex=r'^[a-zA-Z0-9]+$')  # Alphanumeric usernames only
    profile_page: str
    profile_photo: str

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT NOT NULL,
                profile_photo BLOB NOT NULL
            )
        ''')
        conn.commit()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/add_profile", status_code=201)
async def add_profile(
    username: str = File(...),
    profile_page: UploadFile = File(...),
    profile_photo: UploadFile = File(...)
):
    if not username or not profile_page or not profile_photo:
        raise HTTPException(status_code=400, detail="Invalid input")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            profile_page_content = await profile_page.read()
            profile_photo_content = await profile_photo.read()
            cursor.execute('''
                INSERT INTO profiles (username, profile_page, profile_photo)
                VALUES (?, ?, ?)
            ''', (username, profile_page_content, profile_photo_content))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=403, detail="Profile already exists")

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        return row[0]

@app.get("/profile-photo/{username}")
async def get_profile_photo(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Profile photo not found")
        return FileResponse(row[0], media_type='image/png')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)