from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from datetime import datetime

app = FastAPI()

DATABASE = 'db.sqlite3'

# Create the database and the clicks table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

class Click(BaseModel):
    timestamp: datetime

@app.post("/click", status_code=201)
async def register_click(click: Click):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO clicks (timestamp) VALUES (?)', (click.timestamp.isoformat(),))
        conn.commit()
    return {"message": "Click registered successfully"}

@app.get("/clicks")
async def retrieve_clicks(date: str, direction: str):
    if direction not in ["<", ">", "<=", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter")
    
    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute(query, (date,))
        clicks = cursor.fetchall()
    
    if not clicks:
        raise HTTPException(status_code=404, detail="No clicks found")
    
    return [{"id": str(click[0]), "timestamp": click[1]} for click in clicks]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)