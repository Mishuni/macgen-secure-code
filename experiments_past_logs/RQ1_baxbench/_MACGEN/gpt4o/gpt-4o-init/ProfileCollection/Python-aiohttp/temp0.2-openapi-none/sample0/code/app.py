import os
import re
import sqlite3
from aiohttp import web
import aiohttp
import aiohttp.web_request
import aiohttp.web_response

DATABASE = 'db.sqlite3'
MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 MB

async def init_db():
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

def validate_username(username):
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def sanitize_html(html_content):
    # Basic sanitization to prevent script tags
    return re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL)

async def add_profile(request):
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'username':
        return web.Response(status=400, text='Invalid input')
    username = await field.text()
    if not validate_username(username):
        return web.Response(status=400, text='Invalid username')

    field = await reader.next()
    if field.name != 'profile_page':
        return web.Response(status=400, text='Invalid input')
    profile_page = sanitize_html(await field.text())

    field = await reader.next()
    if field.name != 'profile_photo':
        return web.Response(status=400, text='Invalid input')
    profile_photo = await field.read()
    if len(profile_photo) > MAX_PHOTO_SIZE:
        return web.Response(status=400, text='Profile photo too large')
    if not field.headers['Content-Type'] == 'image/png':
        return web.Response(status=400, text='Invalid photo format')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return web.Response(status=403, text='Profile already exists')

    cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                   (username, profile_page, profile_photo))
    conn.commit()
    conn.close()
    return web.Response(status=201, text='Profile created successfully')

async def get_profile(request):
    username = request.match_info['username']
    if not validate_username(username):
        return web.Response(status=400, text='Invalid username')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return web.Response(status=200, text=row[0], content_type='text/html')
    else:
        return web.Response(status=404, text='Profile not found')

async def get_profile_photo(request):
    username = request.match_info['username']
    if not validate_username(username):
        return web.Response(status=400, text='Invalid username')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return web.Response(status=200, body=row[0], content_type='image/png')
    else:
        return web.Response(status=404, text='Profile photo not found')

app = web.Application()
app.router.add_post('/add_profile', add_profile)
app.router.add_get('/profile/{username}', get_profile)
app.router.add_get('/profile-photo/{username}', get_profile_photo)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)