import os
import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import re
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT,
            profile_photo BLOB
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to check if a profile exists
def profile_exists(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM profiles WHERE username = ?', (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Helper function to validate inputs
def validate_input(username, profile_page, profile_photo):
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
        return False, 'Invalid username format'
    if not re.match(r'^https?://[^\s]+$', profile_page):
        return False, 'Invalid profile page URL'
    if not profile_photo.content_type.startswith('image/'):
        return False, 'Invalid profile photo type'
    if profile_photo.size > 2 * 1024 * 1024:  # Limit to 2MB
        return False, 'Profile photo too large'
    return True, ''

# Route to add a new profile
@app.post('/add_profile')
async def add_profile(
    username: str = Form(...),
    profile_page: str = Form(...),
    profile_photo: UploadFile = Form(...)
):
    if not username or not profile_page or not profile_photo:
        raise HTTPException(status_code=400, detail='Invalid input')

    is_valid, message = validate_input(username, profile_page, profile_photo)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    if profile_exists(username):
        raise HTTPException(status_code=403, detail='Profile already exists, creation forbidden')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO profiles (username, profile_page, profile_photo)
        VALUES (?, ?, ?)
    ''', (username, profile_page, profile_photo.file.read()))
    conn.commit()
    conn.close()

    return {'detail': 'Profile created successfully'}

# Route to get a user profile
@app.get('/profile/{username}', response_class=HTMLResponse)
async def get_profile(username: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    else:
        raise HTTPException(status_code=404, detail='Profile not found')

# Route to get a user profile photo
@app.get('/profile-photo/{username}')
async def get_profile_photo(username: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return StreamingResponse(io.BytesIO(row[0]), media_type='image/png')
    else:
        raise HTTPException(status_code=404, detail='Profile photo not found')

# Start the server
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)