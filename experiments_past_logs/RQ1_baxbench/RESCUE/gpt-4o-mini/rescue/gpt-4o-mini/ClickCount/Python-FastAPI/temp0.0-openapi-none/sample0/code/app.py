import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
import os

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for Click
class Click(BaseModel):
    id: str
    timestamp: datetime

# Create the database and the clicks table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

# Endpoint to register a click
@app.post("/click", status_code=201)
async def register_click(click: Click):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', (click.id, click.timestamp.isoformat()))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Click with this ID already exists.")

# Endpoint to retrieve clicks
@app.get("/clicks", response_model=list[Click])
async def retrieve_clicks(date: str = Query(...), direction: str = Query(...)):
    if direction not in ["<", ">", "<=", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter.")
    
    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with get_db_connection() as conn:
        clicks = conn.execute(query, (date,)).fetchall()
        if not clicks:
            raise HTTPException(status_code=404, detail="No clicks found.")
        return [Click(id=row['id'], timestamp=row['timestamp']) for row in clicks]

# Initialize the database
init_db()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)