import os
import sqlite3
from aiohttp import web
from datetime import datetime

DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
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

# Register a click
async def register_click(request):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return web.Response(status=201, text='Click registered successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Retrieve clicks
async def retrieve_clicks(request):
    try:
        date = request.query.get('date')
        direction = request.query.get('direction')
        
        if not date or not direction or direction not in ["<", ">", "<=", ">="]:
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return web.Response(status=404, text='No clicks found')

        clicks = [{'id': str(row[0]), 'timestamp': row[1]} for row in rows]
        return web.json_response(clicks)
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Create the web application
app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

# Initialize the database
init_db()

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)