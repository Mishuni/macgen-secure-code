import os
import json
import logging
from aiohttp import web
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Helper function to get the current time in ISO format
def current_time_iso():
    return datetime.utcnow().isoformat()

# Handler for the /heartbeat endpoint
async def heartbeat(request):
    try:
        data = await request.json()
        service_id = data.get('serviceId')
        token = data.get('token')

        if not service_id or not token:
            return web.Response(status=400, text='Invalid request payload.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            lastNotification=excluded.lastNotification
        ''', (service_id, token, current_time_iso()))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Heartbeat registered successfully.')
    except Exception as e:
        logger.error(f"Error in /heartbeat: {e}")
        return web.Response(status=500, text='Internal server error.')

# Handler for the /services endpoint
async def services(request):
    try:
        data = await request.json()
        token = data.get('token')

        if not token:
            return web.Response(status=400, text='Invalid request payload.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (token,))
        services_list = [{'serviceId': row[0], 'lastNotification': row[1]} for row in cursor.fetchall()]
        conn.close()

        return web.json_response(services_list)
    except Exception as e:
        logger.error(f"Error in /services: {e}")
        return web.Response(status=500, text='Internal server error.')

# Initialize the aiohttp web server
app = web.Application()
app.router.add_post('/heartbeat', heartbeat)
app.router.add_post('/services', services)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)