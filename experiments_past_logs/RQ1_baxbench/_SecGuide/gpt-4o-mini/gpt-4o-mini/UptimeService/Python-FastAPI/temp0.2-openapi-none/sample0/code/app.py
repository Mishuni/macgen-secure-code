from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, constr
import sqlite3
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-trusted-origin.com"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = 'db.sqlite3'

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

class HeartbeatRequest(BaseModel):
    serviceId: constr(min_length=1, max_length=100, regex='^[a-zA-Z0-9]+$')  # Alphanumeric constraint
    token: constr(min_length=1, max_length=100)  # Add length constraints

class ServicesRequest(BaseModel):
    token: constr(min_length=1, max_length=100)  # Add length constraints

@app.post("/heartbeat")
async def register_heartbeat(request: HeartbeatRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (serviceId, token, lastNotification)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(serviceId) DO UPDATE SET
                token=excluded.token,
                lastNotification=datetime('now')
            ''', (request.serviceId, request.token))
            conn.commit()
        return {"message": "Heartbeat registered successfully."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Service ID already exists.")
    except Exception as e:
        # Log the error internally (not shown here for brevity)
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/services")
async def get_services(request: ServicesRequest):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT serviceId, lastNotification FROM services WHERE token = ?
            ''', (request.token,))
            services = cursor.fetchall()
            return [{"serviceId": service[0], "lastNotification": service[1]} for service in services]
    except Exception as e:
        # Log the error internally (not shown here for brevity)
        raise HTTPException(status_code=500, detail="Internal server error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)