import os
import sqlite3
from aiohttp import web
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

# Handlers
async def register_click(request):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return web.Response(status=201, text='Click registered successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

async def retrieve_clicks(request):
    date = request.query.get('date')
    direction = request.query.get('direction')

    if not date or not direction:
        return web.Response(status=400, text='Invalid request')

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return web.Response(status=400, text='Invalid date format, expected YYYY-MM-DD')

    # Validate direction
    if direction not in ["<", ">", "<=", ">="]:
        return web.Response(status=400, text='Invalid direction, expected one of "<", ">", "<=", ">="')

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return web.Response(status=404, text='No clicks found')

        clicks = [{'id': str(row[0]), 'timestamp': row[1]} for row in rows]
        return web.json_response(clicks)
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# App setup
app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)