import aiohttp
from aiohttp import web
import sqlite3
import os
import re

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
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

# Initialize the database
init_db()

# Input validation functions
def is_valid_username(username):
    return isinstance(username, str) and re.match(r'^[a-zA-Z0-9_]+$', username)

def is_valid_html(html):
    return isinstance(html, str) and len(html) > 0

async def add_profile(request):
    data = await request.post()
    username = data.get('username')
    profile_page = data.get('profile_page')
    profile_photo = data.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return web.Response(status=400, text='Invalid input')

    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username format')

    if not is_valid_html(profile_page):
        return web.Response(status=400, text='Invalid HTML content')

    profile_photo_data = await profile_photo.read()

    if not profile_photo_data or not profile_photo.filename.endswith('.png'):
        return web.Response(status=400, text='Invalid profile photo, must be a PNG')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username, profile_page, profile_photo_data))
        conn.commit()
        return web.Response(status=201, text='Profile created successfully')
    except sqlite3.IntegrityError:
        return web.Response(status=403, text='Profile already exists, creation forbidden')
    finally:
        conn.close()

async def get_profile(request):
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    profile = cursor.fetchone()
    
    conn.close()
    
    if profile:
        return web.Response(text=profile[0], content_type='text/html')
    else:
        return web.Response(status=404, text='Profile not found')

async def get_profile_photo(request):
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    profile_photo = cursor.fetchone()
    
    conn.close()
    
    if profile_photo:
        return web.Response(body=profile_photo[0], content_type='image/png')
    else:
        return web.Response(status=404, text='Profile photo not found')

app = web.Application()
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)