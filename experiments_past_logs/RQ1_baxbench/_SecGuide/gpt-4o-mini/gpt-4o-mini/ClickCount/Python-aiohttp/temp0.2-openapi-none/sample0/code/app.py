import aiohttp
from aiohttp import web
import sqlite3
import os
import json
from datetime import datetime
import logging
import re
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError, HTTPNotFound

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

# Set up logging
logging.basicConfig(level=logging.INFO)

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
        logging.error(f"Error registering click: {e}")
        raise HTTPInternalServerError(text="Internal Server Error")

async def retrieve_clicks(request):
    date_str = request.query.get('date')
    direction = request.query.get('direction')

    if not date_str or not direction:
        raise HTTPBadRequest(text="Invalid request")

    # Validate date format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise HTTPBadRequest(text="Invalid date format. Use YYYY-MM-DD.")

    # Validate direction
    valid_directions = {'<', '<=', '>', '>='}
    if direction not in valid_directions:
        raise HTTPBadRequest(text="Invalid direction")

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if direction == '<':
            cursor.execute('SELECT id, timestamp FROM clicks WHERE timestamp < ?', (date.isoformat(),))
        elif direction == '<=':
            cursor.execute('SELECT id, timestamp FROM clicks WHERE timestamp <= ?', (date.isoformat(),))
        elif direction == '>':
            cursor.execute('SELECT id, timestamp FROM clicks WHERE timestamp > ?', (date.isoformat(),))
        elif direction == '>=':
            cursor.execute('SELECT id, timestamp FROM clicks WHERE timestamp >= ?', (date.isoformat(),))

        clicks = cursor.fetchall()
        conn.close()

        if not clicks:
            raise HTTPNotFound(text="No clicks found")

        response_data = [{'id': str(click[0]), 'timestamp': click[1]} for click in clicks]
        return web.json_response(response_data)
    except Exception as e:
        logging.error(f"Error retrieving clicks: {e}")
        raise HTTPInternalServerError(text="Internal Server Error")

app = web.Application()
app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)