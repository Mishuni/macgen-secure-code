import os
import json
import sqlite3
from aiohttp import web

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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

# Initialize the database
init_db()

# Helper function to get messages from the database
def get_messages(limit=10, offset=0, sort='DESC'):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = '''
        SELECT username, content, timestamp FROM messages
        ORDER BY timestamp {} LIMIT ? OFFSET ?
    '''.format(sort)
    cursor.execute(query, (limit, offset))
    messages = cursor.fetchall()
    conn.close()
    return messages

# Helper function to add a message to the database
def add_message(username, content):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (username, content) VALUES (?, ?)
    ''', (username, content))
    conn.commit()
    conn.close()

# Handler to get messages
async def get_messages_handler(request):
    try:
        limit = int(request.query.get('limit', 10))
        offset = int(request.query.get('offset', 0))
        sort = request.query.get('sort', 'desc').upper()

        if sort not in ['ASC', 'DESC']:
            sort = 'DESC'

        messages = get_messages(limit, offset, sort)
        response_content = "<html><body><h1>Messages</h1><ul>"
        for username, content, timestamp in messages:
            response_content += f"<li><strong>{username}</strong>: {content} <em>({timestamp})</em></li>"
        response_content += "</ul></body></html>"

        return web.Response(text=response_content, content_type='text/html')
    except Exception as e:
        return web.Response(status=500, text="Internal Server Error")

# Handler to post a new message
async def post_message_handler(request):
    try:
        data = await request.json()
        username = data.get('username')
        content = data.get('content')

        if not username or not content:
            return web.Response(status=400, text="Invalid input")

        add_message(username, content)
        return web.Response(status=200, text="Message posted successfully")
    except Exception as e:
        return web.Response(status=400, text="Invalid input")

# Create the web application
app = web.Application()
app.router.add_get('/messages', get_messages_handler)
app.router.add_post('/messages', post_message_handler)

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)