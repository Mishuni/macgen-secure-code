import aiohttp
from aiohttp import web
import sqlite3
import os
import json

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Create the web application
app = web.Application()

async def get_messages(request):
    limit = request.query.get('limit', 10)
    offset = request.query.get('offset', 0)
    sort = request.query.get('sort', 'DESC')

    if sort not in ['ASC', 'DESC']:
        return web.Response(status=400, text='Invalid sort parameter')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT username, content, created_at FROM messages
        ORDER BY created_at {sort}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    response_data = [{'username': row[0], 'content': row[1], 'created_at': row[2]} for row in messages]
    return web.json_response(response_data)

async def post_message(request):
    try:
        data = await request.json()
        username = data['username']
        content = data['content']

        if not username or not content:
            return web.Response(status=400, text='Invalid input')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
        conn.commit()
        conn.close()

        return web.Response(status=200)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid input')

# Define routes
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)