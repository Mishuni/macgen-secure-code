import aiohttp
from aiohttp import web
import sqlite3
import json
import os
import html

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

async def get_messages(request):
    limit = int(request.query.get('limit', 10))
    offset = int(request.query.get('offset', 0))
    sort = request.query.get('sort', 'DESC').upper()

    if sort not in ['ASC', 'DESC']:
        return web.Response(status=400, text='Invalid sort parameter')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    order = 'ASC' if sort == 'ASC' else 'DESC'
    cursor.execute('SELECT username, content, created_at FROM messages ORDER BY created_at {} LIMIT ? OFFSET ?'.format(order), (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    response_html = '<html><body><h1>Messages</h1><ul>'
    for username, content, created_at in messages:
        response_html += f'<li><strong>{html.escape(username)}</strong>: {html.escape(content)} <em>({created_at})</em></li>'
    response_html += '</ul></body></html>'

    return web.Response(text=response_html, content_type='text/html')

async def post_message(request):
    try:
        data = await request.json()
        username = data['username']
        content = data['content']
        
        # Basic input validation
        if not isinstance(username, str) or not isinstance(content, str):
            return web.Response(status=400, text='Invalid input')
        
        if len(username) == 0 or len(content) == 0:
            return web.Response(status=400, text='Username and content cannot be empty')
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
    conn.commit()
    conn.close()

    return web.Response(status=200)

app = web.Application()
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)