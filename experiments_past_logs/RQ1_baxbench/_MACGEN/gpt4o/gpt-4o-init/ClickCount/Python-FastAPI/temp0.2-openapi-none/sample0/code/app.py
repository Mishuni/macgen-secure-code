import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi.responses import JSONResponse

app = FastAPI(title="Click Tracking API", version="1.0.0", description="API for registering and retrieving user clicks.")

DATABASE = "db.sqlite3"

class Click(BaseModel):
    id: str
    timestamp: datetime

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/click", status_code=201)
def register_click():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    click_id = os.urandom(16).hex()
    timestamp = datetime.utcnow().isoformat()
    try:
        cursor.execute("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", (click_id, timestamp))
        conn.commit()
    except sqlite3.Error:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid request")
    conn.close()
    return JSONResponse(status_code=201, content={"message": "Click registered successfully"})

@app.get("/clicks", response_model=List[Click])
def retrieve_clicks(date: str = Query(..., description="The date to filter clicks.", example="2022-01-01"), 
                    direction: str = Query(..., description="Specify '<', '<=' or '>' etc. to filter clicks before, before or at or after the date.", enum=["<", ">", "<=", ">="])):
    try:
        filter_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
    cursor.execute(query, (filter_date.isoformat(),))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No clicks found")

    clicks = [Click(id=row[0], timestamp=row[1]) for row in rows]
    return clicks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)