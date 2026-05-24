
import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI(title="Service Monitoring API", version="1.0.0", description="API for monitoring the status of services.")

DATABASE = "db.sqlite3"

# Ensure the database and table exist
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

class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServicesRequest(BaseModel):
    token: str

@app.post("/heartbeat", summary="Register a heartbeat for a service")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification) 
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET 
            lastNotification=excluded.lastNotification
        ''', (request.serviceId, request.token, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return JSONResponse(status_code=200, content={"message": "Heartbeat registered successfully."})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/services", summary="Get overview of registered services")
async def get_services(request: ServicesRequest):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (request.token,))
        services = cursor.fetchall()
        conn.close()
        return JSONResponse(status_code=200, content=[
            {"serviceId": service[0], "lastNotification": service[1]} for service in services
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)