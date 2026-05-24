import os
import sqlite3
from aiohttp import web
from datetime import datetime

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to get query parameters with defaults
def get_query_param(request, name, default=None, cast_type=str):
    value = request.query.get(name, default)
    try:
        return cast_type(value) if value is not None else default
    except ValueError:
        return default

# Handlers
async def get_messages(request):
    limit = get_query_param(request, "limit", 10, int)
    offset = get_query_param(request, "offset", 0, int)
    sort = get_query_param(request, "sort", "DESC", str).upper()
    if sort not in ["ASC", "DESC"]:
        sort = "DESC"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT username, content, created_at 
        FROM messages 
        ORDER BY created_at {sort} 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    # Render messages as HTML
    html = "<html><body><h1>Messages</h1><ul>"
    for row in rows:
        username, content, created_at = row
        html += f"<li><strong>{username}</strong>: {content} <em>({created_at})</em></li>"
    html += "</ul></body></html>"
    return web.Response(text=html, content_type="text/html")

async def post_message(request):
    try:
        data = await request.json()
        username = data.get("username")
        content = data.get("content")

        if not username or not content:
            raise ValueError("Invalid input")

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (username, content, created_at) 
            VALUES (?, ?, ?)
        """, (username, content, created_at))
        conn.commit()
        conn.close()

        return web.Response(text="Message posted successfully", status=200)
    except (ValueError, KeyError):
        return web.Response(text="Invalid input", status=400)

# App setup
app = web.Application()
app.router.add_get('/messages', get_messages)
app.router.add_post('/messages', post_message)

# Start the server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)