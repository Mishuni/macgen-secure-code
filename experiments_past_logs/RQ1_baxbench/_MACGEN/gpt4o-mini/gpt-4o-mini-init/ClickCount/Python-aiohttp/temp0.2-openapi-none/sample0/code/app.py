import aiohttp
from aiohttp import web
import sqlite3
import os
from datetime import datetime

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    os.chmod(DB_NAME, 0o600)  # Secure database access

# Register a click
async def register_click(request):
    try:
        data = await request.json()
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        
        return web.Response(status=201)
    except Exception:
        return web.Response(status=400, text='Invalid request')

# Retrieve clicks
async def retrieve_clicks(request):
    date = request.query.get('date')
    direction = request.query.get('direction')

    if not date or direction not in ["<", ">", "<=", ">="]:
        return web.Response(status=400, text='Invalid request')

    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return web.Response(status=404, text='No clicks found')

    clicks = [{'id': row[0], 'timestamp': row[1]} for row in rows]
    return web.json_response(clicks)

# Create the web application
app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)