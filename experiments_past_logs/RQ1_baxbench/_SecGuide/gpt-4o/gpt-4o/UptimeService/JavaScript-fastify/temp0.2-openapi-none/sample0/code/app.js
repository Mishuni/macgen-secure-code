import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from dotenv import load_dotenv
import uvicorn
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_NAME = os.getenv('DB_NAME')
if not DB_NAME:
    logger.error("Database name must be set in environment variables.")
    raise RuntimeError("Database name must be set in environment variables.")

# Create a new connection for each request to avoid concurrency issues
def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# Create tables if they don't exist
def initialize_database():
    conn = get_db_connection()
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

initialize_database()

# Pydantic models for request validation
class HeartbeatPayload(BaseModel):
    serviceId: str = Field(..., min_length=1)
    token: str = Field(..., min_length=1)

class ServicesPayload(BaseModel):
    token: str = Field(..., min_length=1)

# Register a heartbeat for a service
@app.post('/heartbeat')
async def register_heartbeat(payload: HeartbeatPayload):
    conn = get_db_connection()
    cursor = conn.cursor()
    last_notification = datetime.utcnow().isoformat()

    try:
        cursor.execute('''
        INSERT INTO services (serviceId, token, lastNotification)
        VALUES (?, ?, ?)
        ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification
        ''', (payload.serviceId, payload.token, last_notification))
        conn.commit()
    except Exception as e:
        logger.error(f"Error registering heartbeat: {e}")
        raise HTTPException(status_code=500, detail='Internal server error.')
    finally:
        conn.close()

    return {'message': 'Heartbeat registered successfully.'}

# Get overview of registered services
@app.post('/services')
async def get_services(payload: ServicesPayload):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (payload.token,))
        services = cursor.fetchall()
        services_list = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
    except Exception as e:
        logger.error(f"Error retrieving services: {e}")
        raise HTTPException(status_code=500, detail='Internal server error.')
    finally:
        conn.close()

    return services_list

# Start the server
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)