import os
import json
import sqlite3
from aiohttp import web

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

# Handlers
async def register_heartbeat(request):
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
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(serviceId) DO UPDATE SET
            lastNotification=datetime('now'), token=excluded.token
        ''', (service_id, token))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Heartbeat registered successfully.')
    except sqlite3.Error as e:
        return web.Response(status=500, text=f'Database error: {str(e)}')
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON payload.')
    except Exception as e:
        return web.Response(status=500, text=f'Internal server error: {str(e)}')

async def get_services(request):
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
        services = cursor.fetchall()
        conn.close()

        services_list = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]

        return web.json_response(services_list, status=200)
    except sqlite3.Error as e:
        return web.Response(status=500, text=f'Database error: {str(e)}')
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON payload.')
    except Exception as e:
        return web.Response(status=500, text=f'Internal server error: {str(e)}')

# App setup
app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)