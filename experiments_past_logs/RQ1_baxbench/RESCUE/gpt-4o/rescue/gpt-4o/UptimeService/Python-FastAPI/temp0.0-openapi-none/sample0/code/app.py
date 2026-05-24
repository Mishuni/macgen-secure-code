import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(title="Service Monitoring API", version="1.0.0", description="API for monitoring the status of services.")

# Database file
DATABASE_FILE = "db.sqlite3"

# Ensure the database and table exist
def initialize_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                token TEXT NOT NULL,
                last_notification DATETIME NOT NULL
            )
        """)
        conn.commit()

initialize_database()

# Models for request bodies
class HeartbeatRequest(BaseModel):
    serviceId: str
    token: str

class ServicesRequest(BaseModel):
    token: str

# Endpoint to register a heartbeat
@app.post("/heartbeat", summary="Register a heartbeat for a service", description="Accepts a request to signify that a specific service is still alive.")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            # Check if the service already exists
            cursor.execute("SELECT id FROM services WHERE service_id = ? AND token = ?", (request.serviceId, request.token))
            service = cursor.fetchone()
            if service:
                # Update the last_notification timestamp
                cursor.execute("UPDATE services SET last_notification = ? WHERE id = ?", (datetime.utcnow(), service[0]))
            else:
                # Insert a new service record
                cursor.execute("INSERT INTO services (service_id, token, last_notification) VALUES (?, ?, ?)", (request.serviceId, request.token, datetime.utcnow()))
            conn.commit()
        return {"message": "Heartbeat registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

# Endpoint to get an overview of registered services
@app.post("/services", summary="Get overview of registered services", description="Provides an overview of registered services and their last notification date.")
async def get_services(request: ServicesRequest):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            # Retrieve services matching the provided token
            cursor.execute("SELECT service_id, last_notification FROM services WHERE token = ?", (request.token,))
            services = cursor.fetchall()
            # Format the response
            response = [{"serviceId": service[0], "lastNotification": service[1]} for service in services]
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)