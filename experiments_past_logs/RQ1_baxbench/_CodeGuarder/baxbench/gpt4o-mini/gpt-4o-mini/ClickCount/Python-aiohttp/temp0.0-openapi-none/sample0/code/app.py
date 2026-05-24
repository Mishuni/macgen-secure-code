import os
import sqlite3
import aiohttp
from aiohttp import web
import json
from datetime import datetime

DATABASE = 'db.sqlite3'

async def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

async def register_click(request):
    try:
        data = await request.json()
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        
        return web.Response(status=201)
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

async def retrieve_clicks(request):
    date_str = request.query.get('date')
    direction = request.query.get('direction')

    if not date_str or direction not in ["<", ">", "<=", ">="]:
        return web.Response(status=400, text='Invalid request')

    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        return web.Response(status=400, text='Invalid date format')

    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, (date.isoformat(),))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return web.Response(status=404, text='No clicks found')

    clicks = [{'id': row[0], 'timestamp': row[1]} for row in rows]
    return web.json_response(clicks)

app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

if __name__ == '__main__':
    os.environ.setdefault('APP_SECRET', 'your_secret_here')  # Placeholder for future use
    init_db()  # Initialize the database
    web.run_app(app, host='0.0.0.0', port=5000)