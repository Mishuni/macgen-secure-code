import sqlite3
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE_FILE = 'db.sqlite3'

# Create the database and the services table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                lastNotification TEXT,
                token TEXT
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Pydantic models for request and response
class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServiceOverviewRequest(BaseModel):
    token: str

class ServiceOverviewResponse(BaseModel):
    serviceId: str
    lastNotification: str

# Endpoint to register a heartbeat for a service
@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT INTO services (serviceId, lastNotification, token)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?
        ''', (request.serviceId, now, request.token, now))
        conn.commit()
    return {"message": "Heartbeat registered successfully."}

# Endpoint to get an overview of registered services
@app.post("/services", response_model=List[ServiceOverviewResponse])
async def get_services(request: ServiceOverviewRequest):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (request.token,))
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail="No services found for the provided token.")
        
        services = [ServiceOverviewResponse(serviceId=row[0], lastNotification=row[1]) for row in results]
    return services

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)