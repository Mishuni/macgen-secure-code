import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Models
class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServicesRequest(BaseModel):
    token: str

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints
@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services WHERE serviceId = ? AND token = ?', (request.serviceId, request.token))
        service = cursor.fetchone()
        
        if service:
            cursor.execute('UPDATE services SET lastNotification = ? WHERE serviceId = ?', (datetime.utcnow().isoformat(), request.serviceId))
        else:
            cursor.execute('INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)', (request.serviceId, request.token, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        return {"message": "Heartbeat registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

@app.post("/services")
async def get_services(request: ServicesRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (request.token,))
        services = cursor.fetchall()
        conn.close()
        
        if not services:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No services found for the provided token.")
        
        return [{"serviceId": service["serviceId"], "lastNotification": service["lastNotification"]} for service in services]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)