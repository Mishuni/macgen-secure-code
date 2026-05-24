import aiohttp
from aiohttp import web
import sqlite3
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
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

async def get_messages(request):
    limit = request.query.get('limit', 10)
    offset = request.query.get('offset', 0)
    sort = request.query.get('sort', 'DESC')

    try:
        limit = int(limit)
        offset = int(offset)
        if sort not in ['ASC', 'DESC']:
            sort = 'DESC'
    except ValueError:
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, content FROM messages ORDER BY id ? LIMIT ? OFFSET ?', (sort, limit, offset))
    messages = cursor.fetchall()
    conn.close()

    response_html = '<html><body><h1>Messages</h1><ul>'
    for username, content in messages:
        response_html += f'<li><strong>{html.escape(username)}:</strong> {html.escape(content)}</li>'
    response_html += '</ul></body></html>'
    
    return web.Response(text=response_html, content_type='text/html')

async def post_message(request):
    try:
        data = await request.json()
        username = data['username']
        content = data['content']

        # Input validation
        if not isinstance(username, str) or not isinstance(content, str):
            return web.Response(status=400, text='Invalid input')
        if len(username) > 100 or len(content) > 500:
            return web.Response(status=400, text='Input too long')

        # Sanitize input
        username = html.escape(username)
        content = html.escape(content)

    except (KeyError, ValueError):
        return web.Response(status=400, text='Invalid input')

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
        conn.commit()
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error')
    finally:
        conn.close()

    return web.Response(status=200)

app = web.Application()
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)