
import os
import sqlite3
from aiohttp import web
import json
from jsonschema import validate, ValidationError

# Define JSON schemas for validation
heartbeat_schema = {
    "type": "object",
    "properties": {
        "serviceId": {"type": "string"},
        "token": {"type": "string"}
    },
    "required": ["serviceId", "token"]
}

services_schema = {
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"]
}

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT,
            lastNotification TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Register a heartbeat
async def register_heartbeat(request):
    try:
        data = await request.json()
        validate(instance=data, schema=heartbeat_schema)
    except (json.JSONDecodeError, ValidationError):
        return web.Response(status=400, text="Invalid request payload.")
    
    service_id = data['serviceId']
    token = data['token']
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO services (serviceId, token, lastNotification)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(serviceId) DO UPDATE SET lastNotification=datetime('now')
    ''', (service_id, token))
    conn.commit()
    conn.close()
    
    return web.Response(status=200, text="Heartbeat registered successfully.")

# Get overview of registered services
async def get_services(request):
    try:
        data = await request.json()
        validate(instance=data, schema=services_schema)
    except (json.JSONDecodeError, ValidationError):
        return web.Response(status=400, text="Invalid request payload.")
    
    token = data['token']
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token=?', (token,))
    services = cursor.fetchall()
    conn.close()
    
    services_list = [{"serviceId": service[0], "lastNotification": service[1]} for service in services]
    return web.json_response(services_list)

# Create the web application
app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

# Initialize the database and run the app
init_db()
web.run_app(app, host='0.0.0.0', port=5000)