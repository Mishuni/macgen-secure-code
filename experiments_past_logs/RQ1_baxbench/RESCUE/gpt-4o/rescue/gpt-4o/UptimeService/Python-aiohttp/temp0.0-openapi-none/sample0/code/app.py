import os
import sqlite3
from aiohttp import web
import json
from datetime import datetime

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT NOT NULL,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL,
            PRIMARY KEY (serviceId, token)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function to execute database queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Handlers
async def register_heartbeat(request):
    try:
        # Parse JSON body
        json_data = await request.json()
        service_id = json_data.get("serviceId")
        token = json_data.get("token")

        # Validate input
        if not service_id or not token:
            return web.json_response({"error": "Invalid request payload"}, status=400)

        # Update or insert service heartbeat
        now = datetime.utcnow().isoformat()
        execute_query("""
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId, token) DO UPDATE SET lastNotification=excluded.lastNotification
        """, (service_id, token, now))

        return web.json_response({"message": "Heartbeat registered successfully"}, status=200)
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

async def get_services(request):
    try:
        # Parse JSON body
        json_data = await request.json()
        token = json_data.get("token")

        # Validate input
        if not token:
            return web.json_response({"error": "Invalid request payload"}, status=400)

        # Fetch services for the given token
        services = execute_query("""
            SELECT serviceId, lastNotification FROM services WHERE token = ?
        """, (token,), fetchall=True)

        # Format response
        response_data = [
            {"serviceId": row["serviceId"], "lastNotification": row["lastNotification"]}
            for row in services
        ]

        return web.json_response(response_data, status=200)
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

# App setup
app = web.Application()
app.router.add_post("/heartbeat", register_heartbeat)
app.router.add_post("/services", get_services)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)