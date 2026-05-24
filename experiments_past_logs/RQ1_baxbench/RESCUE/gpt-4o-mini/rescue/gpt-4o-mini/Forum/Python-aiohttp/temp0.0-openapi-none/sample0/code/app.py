import aiohttp
from aiohttp import web
import sqlite3
import os
import json
from html import escape

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
    except ValueError:
        return web.Response(status=400, text='Invalid limit or offset')

    if sort not in ['ASC', 'DESC']:
        return web.Response(status=400, text='Invalid sort parameter')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    order = 'ASC' if sort == 'ASC' else 'DESC'
    cursor.execute(f'SELECT username, content FROM messages ORDER BY id {order} LIMIT ? OFFSET ?', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    response_html = '<html><body>'
    for username, content in messages:
        response_html += f'<p><strong>{escape(username)}:</strong> {escape(content)}</p>'
    response_html += '</body></html>'

    return web.Response(text=response_html, content_type='text/html')

async def post_message(request):
    try:
        data = await request.json()
        username = data['username']
        content = data['content']
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid input')

    if not isinstance(username, str) or not isinstance(content, str):
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (escape(username), escape(content)))
    conn.commit()
    conn.close()

    return web.Response(status=200, text='Message posted successfully')

app = web.Application()
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)