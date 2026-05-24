import os
import sqlite3
from datetime import datetime
from fastify import Fastify
from fastify import FastifyError

# Initialize Fastify app
app = Fastify()

# Database setup
DB_FILE = "db.sqlite3"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serviceId TEXT NOT NULL,
    token TEXT NOT NULL,
    lastNotification TEXT NOT NULL
)
""")
conn.commit()

# Helper function to sanitize input
def sanitize_input(input_str):
    if not isinstance(input_str, str):
        raise ValueError("Invalid input type")
    return input_str.strip()

# Route: Register a heartbeat for a service
@app.post('/heartbeat')
async def register_heartbeat(request, reply):
    try:
        # Parse and validate request body
        body = request.body
        if not body or not isinstance(body, dict):
            return reply.status(400).send({"error": "Invalid request payload"})
        
        service_id = sanitize_input(body.get("serviceId", ""))
        token = sanitize_input(body.get("token", ""))
        
        if not service_id or not token:
            return reply.status(400).send({"error": "Missing required fields"})
        
        # Update or insert service heartbeat
        now = datetime.utcnow().isoformat()
        cursor.execute("""
        INSERT INTO services (serviceId, token, lastNotification)
        VALUES (?, ?, ?)
        ON CONFLICT(serviceId) DO UPDATE SET
        lastNotification = excluded.lastNotification
        WHERE token = excluded.token
        """, (service_id, token, now))
        conn.commit()
        
        return reply.status(200).send({"message": "Heartbeat registered successfully"})
    except Exception as e:
        return reply.status(500).send({"error": "Internal server error"})

# Route: Get overview of registered services
@app.post('/services')
async def get_services(request, reply):
    try:
        # Parse and validate request body
        body = request.body
        if not body or not isinstance(body, dict):
            return reply.status(400).send({"error": "Invalid request payload"})
        
        token = sanitize_input(body.get("token", ""))
        if not token:
            return reply.status(400).send({"error": "Missing required fields"})
        
        # Fetch services matching the token
        cursor.execute("""
        SELECT serviceId, lastNotification FROM services WHERE token = ?
        """, (token,))
        services = cursor.fetchall()
        
        # Format response
        response = [
            {"serviceId": service[0], "lastNotification": service[1]}
            for service in services
        ]
        return reply.status(200).send(response)
    except Exception as e:
        return reply.status(500).send({"error": "Internal server error"})

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")