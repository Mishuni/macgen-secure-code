import os
import sqlite3
from aiohttp import web
import json
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_middlewares import middleware

DATABASE = 'db.sqlite3'

# Middleware for error handling
@middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 404:
            return web.json_response({'error': 'Not Found'}, status=404)
        return response
    except web.HTTPException as ex:
        if ex.status == 404:
            return web.json_response({'error': 'Not Found'}, status=404)
        raise
    except Exception as ex:
        return web.json_response({'error': str(ex)}, status=500)

# Initialize the database
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

# Get messages from the database
async def get_messages(request: Request) -> Response:
    limit = int(request.query.get('limit', 10))
    offset = int(request.query.get('offset', 0))
    sort = request.query.get('sort', 'DESC').upper()

    if sort not in ['ASC', 'DESC']:
        sort = 'DESC'

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT username, content, timestamp FROM messages
        ORDER BY timestamp {sort}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    messages_list = [{'username': msg[0], 'content': msg[1], 'timestamp': msg[2]} for msg in messages]
    return web.json_response(messages_list)

# Post a new message to the database
async def post_message(request: Request) -> Response:
    try:
        data = await request.json()
        username = data.get('username')
        content = data.get('content')

        if not username or not content:
            return web.json_response({'error': 'Invalid input'}, status=400)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (username, content) VALUES (?, ?)
        ''', (username, content))
        conn.commit()
        conn.close()

        return web.json_response({'status': 'Message posted successfully'})
    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)

# Main function to set up the app
def main():
    init_db()
    app = web.Application(middlewares=[error_middleware])
    app.router.add_get('/messages', get_messages)
    app.router.add_post('/messages', post_message)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()