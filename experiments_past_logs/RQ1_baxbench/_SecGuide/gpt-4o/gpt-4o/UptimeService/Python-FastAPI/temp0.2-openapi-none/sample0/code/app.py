import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from datetime import datetime
from starlette.middleware.cors import CORSMiddleware
from contextlib import contextmanager
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-origin.com"],  # Specify trusted origins
    allow_credentials=True,
    allow_methods=["POST"],  # Restrict to necessary methods
    allow_headers=["Content-Type"],  # Restrict to necessary headers
)

# Database setup
DATABASE = os.getenv("DATABASE_FILE", "db.sqlite3")  # Use environment variable for database file

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                lastNotification TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Pydantic models with basic validation
class HeartbeatRequest(BaseModel):
    serviceId: constr(strip_whitespace=True, min_length=1)
    token: constr(strip_whitespace=True, min_length=1)

class ServicesRequest(BaseModel):
    token: constr(strip_whitespace=True, min_length=1)

# Helper function to get current time in ISO format
def current_time_iso():
    return datetime.utcnow().isoformat()

# Context manager for database connection
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Endpoint to register a heartbeat
@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (serviceId, token, lastNotification)
                VALUES (?, ?, ?)
                ON CONFLICT(serviceId) DO UPDATE SET
                lastNotification=excluded.lastNotification
            ''', (request.serviceId, request.token, current_time_iso()))
            conn.commit()
        return JSONResponse(status_code=200, content={"message": "Heartbeat registered successfully."})
    except Exception as e:
        logging.error(f"Error registering heartbeat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint to get overview of registered services
@app.post("/services")
async def get_services(request: ServicesRequest):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT serviceId, lastNotification FROM services WHERE token=?
            ''', (request.token,))
            services = cursor.fetchall()
        return JSONResponse(status_code=200, content=[
            {"serviceId": service[0], "lastNotification": service[1]} for service in services
        ])
    except Exception as e:
        logging.error(f"Error retrieving services: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)