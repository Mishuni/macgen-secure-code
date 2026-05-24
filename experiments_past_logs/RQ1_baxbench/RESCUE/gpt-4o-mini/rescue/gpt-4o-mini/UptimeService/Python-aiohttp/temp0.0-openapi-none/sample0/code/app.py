import sqlite3
import json
from aiohttp import web

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            lastNotification TEXT,
            token TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Register a heartbeat for a service
async def register_heartbeat(request):
    try:
        data = await request.json()
        service_id = data['serviceId']
        token = data['token']

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO services (serviceId, lastNotification, token)
            VALUES (?, datetime('now'), ?)
            ON CONFLICT(serviceId) DO UPDATE SET lastNotification = datetime('now')
        ''', (service_id, token))
        
        conn.commit()
        conn.close()
        
        return web.Response(status=200, text='Heartbeat registered successfully.')
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request payload.')
    except Exception as e:
        return web.Response(status=500, text='Internal server error.')

# Get overview of registered services
async def get_services(request):
    try:
        data = await request.json()
        token = data['token']

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()
        
        conn.close()
        
        response_data = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
        return web.json_response(response_data)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request payload.')
    except Exception as e:
        return web.Response(status=500, text='Internal server error.')

# Create the web application
app = web.Application()
app.router.add_post('/heartbeat', register_heartbeat)
app.router.add_post('/services', get_services)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)