from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3
import os
from datetime import datetime

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                lastNotification TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Pydantic models
class HeartbeatRequest(BaseModel):
    serviceId: str = Field(..., description="The unique identifier of the service.")
    token: str = Field(..., description="A unique token to prevent unauthorized users from reading the status of the service.")

class ServicesRequest(BaseModel):
    token: str = Field(..., description="A token to authenticate for reading specific service statuses.")

class ServiceResponse(BaseModel):
    serviceId: str
    lastNotification: str

@app.post("/heartbeat", status_code=200)
async def register_heartbeat(request: HeartbeatRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (serviceId, lastNotification) 
                VALUES (?, ?) 
                ON CONFLICT(serviceId) 
                DO UPDATE SET lastNotification=excluded.lastNotification
            ''', (request.serviceId, datetime.utcnow().isoformat()))
            conn.commit()
        return {"message": "Heartbeat registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/services", response_model=list[ServiceResponse], status_code=200)
async def get_services(request: ServicesRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT serviceId, lastNotification FROM services')
            services = cursor.fetchall()
            return [{"serviceId": service[0], "lastNotification": service[1]} for service in services]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)