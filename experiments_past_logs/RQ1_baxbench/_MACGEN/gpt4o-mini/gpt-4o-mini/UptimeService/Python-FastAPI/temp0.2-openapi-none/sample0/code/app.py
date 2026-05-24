from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()

init_db()

class HeartbeatRequest(BaseModel):
    serviceId: str = Field(..., description="The unique identifier of the service.")
    token: str = Field(..., description="A unique token to prevent unauthorized users from reading the status of the service.")

class ServicesRequest(BaseModel):
    token: str = Field(..., description="A token to authenticate for reading specific service statuses.")

@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    with sqlite3.connect(DATABASE) as conn:
        try:
            conn.execute('''
                INSERT INTO services (serviceId, token) VALUES (?, ?)
                ON CONFLICT(serviceId) DO UPDATE SET lastNotification = CURRENT_TIMESTAMP
            ''', (request.serviceId, request.token))
            conn.commit()
            return {"message": "Heartbeat registered successfully."}
        except Exception:
            raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/services")
async def get_services(request: ServicesRequest):
    with sqlite3.connect(DATABASE) as conn:
        try:
            cursor = conn.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (request.token,))
            services = cursor.fetchall()
            return [{"serviceId": service[0], "lastNotification": service[1]} for service in services]
        except Exception:
            raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)