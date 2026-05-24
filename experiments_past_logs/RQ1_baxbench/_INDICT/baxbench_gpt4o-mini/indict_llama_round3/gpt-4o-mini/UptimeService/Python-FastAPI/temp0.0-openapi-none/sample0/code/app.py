from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                lastNotification TEXT,
                token TEXT
            )
        ''')
        conn.commit()

init_db()

class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServicesRequest(BaseModel):
    token: str

class ServiceStatus(BaseModel):
    serviceId: str
    lastNotification: str

@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Check if the token is valid
            cursor.execute('SELECT token FROM services WHERE serviceId = ?', (request.serviceId,))
            existing_service = cursor.fetchone()
            if existing_service and existing_service[0] != request.token:
                raise HTTPException(status_code=403, detail="Invalid token for this service.")
            
            cursor.execute('''
                INSERT INTO services (serviceId, lastNotification, token)
                VALUES (?, datetime('now'), ?)
                ON CONFLICT(serviceId) DO UPDATE SET lastNotification = datetime('now'), token = ?
            ''', (request.serviceId, request.token, request.token))
            conn.commit()
        return {"message": "Heartbeat registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/services", response_model=list[ServiceStatus])
async def get_services(request: ServicesRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT serviceId, lastNotification FROM services WHERE token = ?
            ''', (request.token,))
            services = cursor.fetchall()
            return [{"serviceId": serviceId, "lastNotification": lastNotification} for serviceId, lastNotification in services]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)