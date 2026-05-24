import os
import sqlite3
from aiohttp import web
import aiohttp
import aiohttp.web_request
import aiohttp.web_response
from aiohttp import web_middlewares
import magic  # For file type validation

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        profile_page TEXT,
        profile_photo BLOB,
        photo_content_type TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Helper function to validate username
def is_valid_username(username):
    return username.isalnum() and 3 <= len(username) <= 30

# Helper function to validate profile page content
def is_valid_profile_page(profile_page):
    # Basic validation to ensure no HTML/JS injection
    return len(profile_page) <= 1000 and '<script>' not in profile_page

# Middleware for database connection management
@web_middlewares.middleware
async def db_middleware(request, handler):
    request['conn'] = sqlite3.connect('db.sqlite3')
    request['cursor'] = request['conn'].cursor()
    try:
        response = await handler(request)
        return response
    finally:
        request['conn'].close()

# Add profile handler
async def add_profile(request):
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'username':
        return web.Response(status=400, text='Invalid input')
    username = await field.text()
    
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username')

    field = await reader.next()
    if field.name != 'profile_page':
        return web.Response(status=400, text='Invalid input')
    profile_page = await field.text()

    if not is_valid_profile_page(profile_page):
        return web.Response(status=400, text='Invalid profile page content')

    field = await reader.next()
    if field.name != 'profile_photo':
        return web.Response(status=400, text='Invalid input')
    
    # Limit file size to 1MB
    profile_photo = await field.read()
    if len(profile_photo) > 1024 * 1024:
        return web.Response(status=400, text='File too large')

    # Validate file type using magic library
    mime = magic.Magic(mime=True)
    actual_content_type = mime.from_buffer(profile_photo)
    if not actual_content_type.startswith('image/'):
        return web.Response(status=400, text='Invalid file type')

    cursor = request['cursor']
    cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
    if cursor.fetchone():
        return web.Response(status=403, text='Profile already exists')

    cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo, photo_content_type) VALUES (?, ?, ?, ?)',
                   (username, profile_page, profile_photo, actual_content_type))
    request['conn'].commit()
    return web.Response(status=201, text='Profile created successfully')

# Get profile handler
async def get_profile(request):
    username = request.match_info['username']
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username')

    cursor = request['cursor']
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        return web.Response(status=200, text=row[0], content_type='text/plain')
    else:
        return web.Response(status=404, text='Profile not found')

# Get profile photo handler
async def get_profile_photo(request):
    username = request.match_info['username']
    if not is_valid_username(username):
        return web.Response(status=400, text='Invalid username')

    cursor = request['cursor']
    cursor.execute('SELECT profile_photo, photo_content_type FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        return web.Response(status=200, body=row[0], content_type=row[1])
    else:
        return web.Response(status=404, text='Profile photo not found')

# Create the web application
app = web.Application(middlewares=[db_middleware])
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

# Run the web server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)