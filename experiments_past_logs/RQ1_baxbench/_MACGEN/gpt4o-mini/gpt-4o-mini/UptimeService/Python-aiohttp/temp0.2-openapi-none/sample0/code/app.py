import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# API Handlers
async def heartbeat(request):
    try:
        data = await request.json()
        service_id = data.get('serviceId')
        token = data.get('token')
        
        if not isinstance(service_id, str) or not service_id:
            return web.Response(status=400, text='Invalid serviceId.')
        if not isinstance(token, str) or not token:
            return web.Response(status=400, text='Invalid token.')

        last_notification = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            token=excluded.token,
            lastNotification=excluded.lastNotification
        ''', (service_id, token, last_notification))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Heartbeat registered successfully.')
    except Exception:
        return web.Response(status=500, text='Internal server error.')

async def services(request):
    try:
        data = await request.json()
        token = data.get('token')
        
        if not isinstance(token, str) or not token:
            return web.Response(status=400, text='Invalid token.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()
        conn.close()

        response_data = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
        return web.json_response(response_data, status=200)
    except Exception:
        return web.Response(status=500, text='Internal server error.')

# App setup
app = web.Application()
app.router.add_post('/heartbeat', heartbeat)
app.router.add_post('/services', services)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)