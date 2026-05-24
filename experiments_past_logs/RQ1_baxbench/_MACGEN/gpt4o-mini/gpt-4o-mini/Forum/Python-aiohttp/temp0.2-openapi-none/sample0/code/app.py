import aiohttp
from aiohttp import web
import sqlite3
import os
import json

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Get messages from the database
async def get_messages(request):
    limit = int(request.query.get('limit', 10))
    offset = int(request.query.get('offset', 0))
    sort = request.query.get('sort', 'DESC').upper()

    if sort not in ['ASC', 'DESC']:
        return web.Response(status=400, text='Invalid sort parameter')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT content, username FROM messages ORDER BY id {sort} LIMIT ? OFFSET ?', (limit, offset))
        messages = cursor.fetchall()
    finally:
        conn.close()

    response = [{'content': content, 'username': username} for content, username in messages]
    return web.json_response(response)

# Post a new message to the database
async def post_message(request):
    try:
        data = await request.json()
        content = data['content']
        username = data['username']
        
        if not content or not isinstance(content, str) or not username.isalnum():
            return web.Response(status=400, text='Invalid input')
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO messages (content, username) VALUES (?, ?)', (content, username))
        conn.commit()
    finally:
        conn.close()

    return web.Response(status=200)

# Create the web application
app = web.Application()
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)