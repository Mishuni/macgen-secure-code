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
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

async def register_heartbeat(request):
    try:
        data = await request.json()
        service_id = data.get('serviceId')
        token = data.get('token')
        
        if not service_id or not token:
            return web.Response(status=400, text='Invalid request payload.')

        last_notification = datetime.utcnow().isoformat()  # Use current time for lastNotification
        
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
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return web.Response(status=500, text='Internal server error.')

async def get_services(request):
    try:
        data = await request.json()
        token = data.get('token')
        
        if not token:
            return web.Response(status=400, text='Invalid request payload.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()
        conn.close()

        response_data = [
            {'serviceId': service_id, 'lastNotification': last_notification}
            for service_id, last_notification in services
        ]

        return web.json_response(response_data, status=200)
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return web.Response(status=500, text='Internal server error.')

app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)