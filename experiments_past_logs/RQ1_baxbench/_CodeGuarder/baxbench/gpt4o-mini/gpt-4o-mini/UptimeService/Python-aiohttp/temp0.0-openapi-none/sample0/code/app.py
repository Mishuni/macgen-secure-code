import aiohttp
from aiohttp import web
import sqlite3
import os
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

# Initialize the database
init_db()

# Helper function to validate JSON payload
def validate_json_payload(data, required_fields):
    if not isinstance(data, dict):
        return False
    return all(field in data for field in required_fields)

# Heartbeat endpoint
async def heartbeat(request):
    try:
        data = await request.json()
        if not validate_json_payload(data, ['serviceId', 'token']):
            return web.Response(status=400, text='Invalid request payload.')

        service_id = data['serviceId']
        token = data['token']
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            token=excluded.token,
            lastNotification=excluded.lastNotification
        ''', (service_id, token, timestamp))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Heartbeat registered successfully.')
    except Exception as e:
        return web.Response(status=500, text='Internal server error.')

# Services overview endpoint
async def services(request):
    try:
        data = await request.json()
        if not validate_json_payload(data, ['token']):
            return web.Response(status=400, text='Invalid request payload.')

        token = data['token']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()
        conn.close()

        response_data = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
        return web.json_response(response_data, status=200)
    except Exception as e:
        return web.Response(status=500, text='Internal server error.')

# Main application setup
app = web.Application()
app.router.add_post('/heartbeat', heartbeat)
app.router.add_post('/services', services)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)