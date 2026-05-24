import aiohttp
from aiohttp import web
import sqlite3
import os
from datetime import datetime

# Database setup
DB_NAME = 'db.sqlite3'

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

# Initialize the database
init_db()

async def register_click(request):
    try:
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return web.Response(status=201)
    except Exception as e:
        return web.Response(status=400, text=str(e))

async def retrieve_clicks(request):
    date_str = request.query.get('date')
    direction = request.query.get('direction')

    if not date_str or direction not in ["<", ">", "<=", ">="]:
        return web.Response(status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        date_iso = date.isoformat()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
        cursor.execute(query, (date_iso,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return web.Response(status=404)

        clicks = [{'id': row[0], 'timestamp': row[1]} for row in rows]
        return web.json_response(clicks)
    except Exception as e:
        return web.Response(status=400, text=str(e))

app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)