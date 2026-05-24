import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

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

def is_valid_service_id(service_id):
    # Validate serviceId (e.g., alphanumeric and length check)
    return isinstance(service_id, str) and re.match(r'^[a-zA-Z0-9_-]{1,50}$', service_id)

def is_valid_token(token):
    # Validate token (e.g., alphanumeric and length check)
    return isinstance(token, str) and re.match(r'^[a-zA-Z0-9_-]{1,100}$', token)

async def register_heartbeat(request):
    try:
        data = await request.json()
        service_id = data.get('serviceId')
        token = data.get('token')
        
        if not service_id or not token or not is_valid_service_id(service_id) or not is_valid_token(token):
            return web.Response(status=400, text='Invalid request payload.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification) 
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(serviceId) 
            DO UPDATE SET token = ?, lastNotification = datetime('now')
        ''', (service_id, token, token))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Heartbeat registered successfully.')
    except Exception as e:
        # Log the error for internal monitoring (not shown here for brevity)
        print(f"Error in register_heartbeat: {e}")  # Internal logging
        return web.Response(status=500, text='Internal server error.')

async def get_services(request):
    try:
        data = await request.json()
        token = data.get('token')
        
        if not token or not is_valid_token(token):
            return web.Response(status=400, text='Invalid request payload.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()
        conn.close()

        response_data = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
        return web.json_response(response_data, status=200)
    except Exception as e:
        # Log the error for internal monitoring (not shown here for brevity)
        print(f"Error in get_services: {e}")  # Internal logging
        return web.Response(status=500, text='Internal server error.')

app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)