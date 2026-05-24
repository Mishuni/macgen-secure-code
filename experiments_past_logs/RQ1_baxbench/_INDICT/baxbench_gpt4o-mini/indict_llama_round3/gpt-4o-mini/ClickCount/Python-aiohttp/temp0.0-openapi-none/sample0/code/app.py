import aiohttp
from aiohttp import web
import sqlite3
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
        # Register a click
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return web.Response(status=201)
    except Exception as e:
        print(f"Error registering click: {e}")
        return web.Response(status=400)

async def retrieve_clicks(request):
    try:
        # Retrieve clicks based on query parameters
        date_str = request.query.get('date')
        direction = request.query.get('direction')

        if not date_str or not direction or direction not in ["<", ">", "<=", ">="]:
            return web.Response(status=400, text="Invalid request")

        date = datetime.strptime(date_str, '%Y-%m-%d')
        date_iso = date.isoformat()

        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, (date_iso,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return web.Response(status=404, text="No clicks found")

        clicks = [{"id": row[0], "timestamp": row[1]} for row in rows]
        return web.json_response(clicks)
    except Exception as e:
        print(f"Error retrieving clicks: {e}")
        return web.Response(status=400)

app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)