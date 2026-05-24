import os
import json
import sqlite3
from aiohttp import web
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

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

# Helper function to validate request data
def validate_request_data(data, required_fields):
    return all(field in data for field in required_fields)

# Helper function to validate input format
def is_valid_input(service_id, token):
    service_id_pattern = r'^[a-zA-Z0-9_-]{1,100}$'
    token_pattern = r'^[a-zA-Z0-9]{1,100}$'
    return (re.match(service_id_pattern, service_id) is not None and
            re.match(token_pattern, token) is not None)

# Routes
async def register_heartbeat(request):
    try:
        data = await request.json()
        if not validate_request_data(data, ['serviceId', 'token']):
            return web.Response(status=400, text='Invalid request payload.')

        service_id = data['serviceId']
        token = data['token']

        if not is_valid_input(service_id, token):
            return web.Response(status=400, text='Invalid input format.')

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
    except Exception as e:
        logging.error(f"Error in register_heartbeat: {e}")
        return web.Response(status=500, text='Internal server error.')

async def get_services(request):
    try:
        data = await request.json()
        if not validate_request_data(data, ['token']):
            return web.Response(status=400, text='Invalid request payload.')

        token = data['token']

        if not isinstance(token, str) or len(token) == 0:
            return web.Response(status=400, text='Invalid token format.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (token,))
        services = cursor.fetchall()
        conn.close()

        services_list = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]

        return web.json_response(services_list, status=200)
    except Exception as e:
        logging.error(f"Error in get_services: {e}")
        return web.Response(status=500, text='Internal server error.')

# Application setup
app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)