import aiohttp
from aiohttp import web
import sqlite3
import os
import mimetypes

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

def is_valid_username(username):
    return isinstance(username, str) and 1 <= len(username) <= 30

def is_valid_profile_page(profile_page):
    return isinstance(profile_page, str) and 1 <= len(profile_page) <= 500

def is_valid_file_type(file_name):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in allowed_extensions

def is_valid_file_content(file_content, file_name):
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type in ['image/png', 'image/jpeg', 'image/gif']

async def add_profile(request):
    reader = await request.multipart()
    username = await reader.next()
    profile_page = await reader.next()
    profile_photo = await reader.next()

    username_value = username.value
    profile_page_value = await profile_page.read()
    profile_photo_value = await profile_photo.read()

    # Validate inputs
    if not is_valid_username(username_value):
        return web.Response(status=400, text='Invalid username')
    if not is_valid_profile_page(profile_page_value.decode('utf-8')):
        return web.Response(status=400, text='Invalid profile page')
    if not is_valid_file_type(profile_photo.filename):
        return web.Response(status=400, text='Invalid file type')
    if not is_valid_file_content(profile_photo_value, profile_photo.filename):
        return web.Response(status=400, text='Invalid file content')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username_value, profile_page_value.decode('utf-8'), profile_photo_value))
        conn.commit()
        return web.Response(status=201, text='Profile created successfully')
    except sqlite3.IntegrityError:
        return web.Response(status=403, text='Profile already exists, creation forbidden')
    except Exception as e:
        return web.Response(status=400, text='Invalid input')
    finally:
        conn.close()

async def get_profile(request):
    username = request.match_info['username']
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username')

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
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    photo = cursor.fetchone()
    conn.close()

    if photo:
        return web.Response(body=photo[0], content_type='image/png')
    else:
        return web.Response(status=404, text='Profile photo not found')

app = web.Application()
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)