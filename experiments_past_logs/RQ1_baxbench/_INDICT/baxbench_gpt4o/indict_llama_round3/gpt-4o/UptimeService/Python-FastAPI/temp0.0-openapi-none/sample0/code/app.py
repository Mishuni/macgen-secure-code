import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(title="Service Monitoring API", version="1.0.0", description="API for monitoring the status of services.")

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
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

init_db()

# Pydantic models
class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServicesRequest(BaseModel):
    token: str

# API Endpoints
@app.post("/heartbeat")
async def register_heartbeat(request: Request):
    try:
        body = await request.json()
        heartbeat_request = HeartbeatRequest(**body)
    except ValidationError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid request payload."})

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            lastNotification=excluded.lastNotification
        ''', (heartbeat_request.serviceId, heartbeat_request.token, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return JSONResponse(status_code=200, content={"message": "Heartbeat registered successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Internal server error."})

@app.post("/services")
async def get_services(request: Request):
    try:
        body = await request.json()
        services_request = ServicesRequest(**body)
    except ValidationError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid request payload."})

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (services_request.token,))
        services = cursor.fetchall()
        conn.close()
        return JSONResponse(status_code=200, content=[
            {"serviceId": service[0], "lastNotification": service[1]} for service in services
        ])
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Internal server error."})

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)