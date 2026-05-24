import aiohttp
from aiohttp import web
import sqlite3
import os
import re
from html import escape

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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

# Sanitize HTML input
def sanitize_html(html_content):
    allowed_tags = ['b', 'i', 'u', 'a']
    sanitized_content = escape(html_content)
    for tag in allowed_tags:
        sanitized_content = sanitized_content.replace(f'&lt;{tag}&gt;', f'<{tag}>').replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    return sanitized_content

# Validate username
def validate_username(username):
    return re.match("^[a-zA-Z0-9_]+$", username) is not None

# Add a new user profile
async def add_profile(request):
    data = await request.post()
    username = data.get('username')
    profile_page = data.get('profile_page')
    profile_photo = data.get('profile_photo').file.read()

    if not username or not profile_page or not profile_photo:
        return web.Response(status=400, text='Invalid input')

    if not validate_username(username):
        return web.Response(status=400, text='Invalid username')

    profile_page = sanitize_html(profile_page)

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username, profile_page, profile_photo))
        conn.commit()
        return web.Response(status=201, text='Profile created successfully')
    except sqlite3.IntegrityError:
        return web.Response(status=403, text='Profile already exists, creation forbidden')
    finally:
        conn.close()

# Get user profile
async def get_profile(request):
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    profile = cursor.fetchone()
    conn.close()

    if profile:
        return web.Response(text=profile[0], content_type='text/html')
    else:
        return web.Response(status=404, text='Profile not found')

# Get user profile photo
async def get_profile_photo(request):
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    photo = cursor.fetchone()
    conn.close()

    if photo:
        return web.Response(body=photo[0], content_type='image/png')
    else:
        return web.Response(status=404, text='Profile photo not found')

# Set up the web application
app = web.Application()
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)