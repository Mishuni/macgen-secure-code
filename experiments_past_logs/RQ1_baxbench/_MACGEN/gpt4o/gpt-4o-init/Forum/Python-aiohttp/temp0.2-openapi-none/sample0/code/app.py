
import os
import json
import sqlite3
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def get_messages(request: Request) -> Response:
    limit = int(request.query.get('limit', 10))
    offset = int(request.query.get('offset', 0))
    sort = request.query.get('sort', 'DESC').upper()

    if sort not in ['ASC', 'DESC']:
        sort = 'DESC'

    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT username, content, timestamp FROM messages
        ORDER BY timestamp {sort}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    html_content = "<html><body><h1>Messages</h1><ul>"
    for username, content, timestamp in messages:
        html_content += f"<li><strong>{username}</strong>: {content} <em>at {timestamp}</em></li>"
    html_content += "</ul></body></html>"

    return web.Response(text=html_content, content_type='text/html')

async def post_message(request: Request) -> Response:
    try:
        data = await request.json()
        username = data['username']
        content = data['content']
    except (json.JSONDecodeError, KeyError):
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (username, content) VALUES (?, ?)
    ''', (username, content))
    conn.commit()
    conn.close()

    return web.Response(status=200, text='Message posted successfully')

def create_app():
    app = web.Application()
    app.router.add_get('/messages', get_messages)
    app.router.add_post('/messages', post_message)
    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5000)