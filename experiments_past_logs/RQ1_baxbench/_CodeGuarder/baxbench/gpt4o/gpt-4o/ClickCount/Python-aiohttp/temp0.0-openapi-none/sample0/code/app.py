import os
import sqlite3
from aiohttp import web
from datetime import datetime
from aiohttp.web import json_response
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound

DATABASE = 'db.sqlite3'

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

async def handle_click(request):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return web.Response(status=201, text='Click registered successfully')
    except Exception as e:
        return HTTPBadRequest(reason=str(e))

async def handle_clicks(request):
    try:
        date = request.query.get('date')
        direction = request.query.get('direction')

        if not date or not direction:
            raise HTTPBadRequest(reason="Missing 'date' or 'direction' query parameter")

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPBadRequest(reason="Invalid date format, expected YYYY-MM-DD")

        if direction not in ['<', '>', '<=', '>=']:
            raise HTTPBadRequest(reason="Invalid direction, expected one of '<', '>', '<=', '>='")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            raise HTTPNotFound(reason="No clicks found")

        clicks = [{'id': str(row[0]), 'timestamp': row[1]} for row in rows]
        return json_response(clicks)
    except HTTPBadRequest as e:
        return e
    except HTTPNotFound as e:
        return e
    except Exception as e:
        return HTTPBadRequest(reason=str(e))

def get_app():
    app = web.Application()
    app.router.add_post('/click', handle_click)
    app.router.add_get('/clicks', handle_clicks)
    return app

if __name__ == '__main__':
    init_db()
    app = get_app()
    web.run_app(app, host='0.0.0.0', port=5000)