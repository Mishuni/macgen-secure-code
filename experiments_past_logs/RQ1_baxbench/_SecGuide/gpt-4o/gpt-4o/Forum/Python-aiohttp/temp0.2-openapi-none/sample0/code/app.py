import os
import sqlite3
import html
from aiohttp import web
import json
from contextlib import closing
from aiohttp.web_middlewares import normalize_path_middleware

# Database setup
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
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

# Initialize the database
init_db()

# Handlers
async def get_messages(request):
    try:
        limit = int(request.query.get('limit', 10))
        offset = int(request.query.get('offset', 0))
        sort = request.query.get('sort', 'DESC').upper()

        if sort not in ['ASC', 'DESC']:
            sort = 'DESC'

        with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, content, created_at FROM messages
                ORDER BY created_at {}
                LIMIT ? OFFSET ?
            '''.format(sort), (limit, offset))
            messages = cursor.fetchall()

        # Escape output to prevent XSS
        escaped_messages = [
            {
                'username': html.escape(username),
                'content': html.escape(content),
                'created_at': created_at
            }
            for username, content, created_at in messages
        ]

        # Render messages as HTML
        html_content = "<html><body><h1>Messages</h1><ul>"
        for msg in escaped_messages:
            html_content += f"<li><strong>{msg['username']}</strong>: {msg['content']} <em>at {msg['created_at']}</em></li>"
        html_content += "</ul></body></html>"

        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in get_messages: {e}")
        return web.Response(status=500, text='Internal Server Error')

async def post_message(request):
    try:
        data = await request.json()
        username = data.get('username', '').strip()
        content = data.get('content', '').strip()

        # Validate input
        if not username or not content or len(username) > 255 or len(content) > 1000:
            return web.Response(status=400, text='Invalid input')

        with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (username, content) VALUES (?, ?)
            ''', (username, content))
            conn.commit()

        return web.Response(status=200, text='Message posted successfully')
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in post_message: {e}")
        return web.Response(status=500, text='Internal Server Error')

# App setup
app = web.Application(middlewares=[normalize_path_middleware()])
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)