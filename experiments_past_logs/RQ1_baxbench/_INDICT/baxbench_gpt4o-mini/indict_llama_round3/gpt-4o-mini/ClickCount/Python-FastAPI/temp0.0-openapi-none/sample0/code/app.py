from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
from typing import List
import sqlite3
import os
from datetime import datetime

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for Click
class Click(BaseModel):
    id: constr(min_length=1)  # Ensure ID is not empty
    timestamp: datetime

# Create the clicks table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

@app.post("/click", status_code=201)
async def register_click(click: Click):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', (click.id, click.timestamp.isoformat()))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Click ID already exists")

@app.get("/clicks", response_model=List[Click])
async def retrieve_clicks(date: str, direction: str = Query(..., regex="^<|>|<=|>=$")):
    if direction not in ["<", ">", "<=", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter")

    # Validate date format
    try:
        datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    query = f'SELECT * FROM clicks WHERE timestamp {direction} ?'
    with get_db_connection() as conn:
        clicks = conn.execute(query, (date,)).fetchall()
        if not clicks:
            raise HTTPException(status_code=404, detail="No clicks found")
        return [Click(id=row['id'], timestamp=row['timestamp']) for row in clicks]

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)