from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
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
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

class Click(BaseModel):
    id: int
    timestamp: datetime

@app.post("/click", status_code=201)
async def register_click(click: Click):
    if not isinstance(click.timestamp, datetime):
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (click.timestamp.isoformat(),))
        conn.commit()
    
    return {"id": cursor.lastrowid, "timestamp": click.timestamp.isoformat()}

@app.get("/clicks", response_model=list[Click])
async def get_clicks(date: str = Query(..., regex=r'^\d{4}-\d{2}-\d{2}$'), direction: str = Query(..., regex=r'^[<>]=?$')):
    if direction not in ["<", ">", "<=", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter")
    
    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No clicks found")
    
    return [{"id": row[0], "timestamp": row[1]} for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)