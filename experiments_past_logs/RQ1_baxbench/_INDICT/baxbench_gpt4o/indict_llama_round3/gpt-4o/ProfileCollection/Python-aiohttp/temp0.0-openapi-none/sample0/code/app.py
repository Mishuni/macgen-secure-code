import os
import sqlite3
from aiohttp import web
import aiohttp
import re

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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

# Validate username
def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

# Validate if the content is a valid PNG
def is_valid_png(data):
    return data.startswith(b'\x89PNG\r\n\x1a\n')

# Add a new profile
async def add_profile(request):
    reader = await request.multipart()
    
    field = await reader.next()
    if field.name != 'username':
        return web.Response(status=400, text='Invalid input')
    username = await field.text()
    
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username format')
    
    field = await reader.next()
    if field.name != 'profile_page':
        return web.Response(status=400, text='Invalid input')
    profile_page = await field.text()
    
    field = await reader.next()
    if field.name != 'profile_photo':
        return web.Response(status=400, text='Invalid input')
    profile_photo = await field.read()
    
    if not is_valid_png(profile_photo):
        return web.Response(status=400, text='Invalid profile photo format')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
        if cursor.fetchone():
            return web.Response(status=403, text='Profile already exists, creation forbidden')
        
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username, profile_page, profile_photo))
        conn.commit()
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error: ' + str(e))
    finally:
        conn.close()
    
    return web.Response(status=201, text='Profile created successfully')

# Get a user profile
async def get_profile(request):
    username = request.match_info['username']
    
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username format')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error: ' + str(e))
    finally:
        conn.close()
    
    if row:
        return web.Response(status=200, text=row[0], content_type='text/html')
    else:
        return web.Response(status=404, text='Profile not found')

# Get a user profile photo
async def get_profile_photo(request):
    username = request.match_info['username']
    
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username format')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error: ' + str(e))
    finally:
        conn.close()
    
    if row:
        return web.Response(status=200, body=row[0], content_type='image/png')
    else:
        return web.Response(status=404, text='Profile photo not found')

# Create the web application
app = web.Application()
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

# Initialize the database and run the app
init_db()
web.run_app(app, host='0.0.0.0', port=5000)