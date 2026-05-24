from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, Response
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

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
async def add_profile(username: str, profile_page: str = File(...), profile_photo: UploadFile = File(...)):
    if not username or not profile_page or not profile_photo:
        raise HTTPException(status_code=400, detail="Invalid input")

    profile_photo_data = await profile_photo.read()
    if len(profile_photo_data) > 2 * 1024 * 1024:  # Limit photo size to 2MB
        raise HTTPException(status_code=400, detail="Profile photo too large")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                           (username, profile_page, profile_photo_data))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=403, detail="Profile already exists, creation forbidden")

    return {"message": "Profile created successfully"}

@app.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile[0]

@app.get("/profile-photo/{username}")
async def get_profile_photo(username: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        profile_photo = cursor.fetchone()
        if profile_photo is None:
            raise HTTPException(status_code=404, detail="Profile photo not found")
        return Response(content=profile_photo[0], media_type='image/png')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)