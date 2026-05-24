import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from starlette.responses import JSONResponse
from sqlite3 import Connection, Cursor
from fastapi.logger import logger
import logging

# Initialize FastAPI app
app = FastAPI(title="Click Tracking API", version="1.0.0", description="API for registering and retrieving user clicks.")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection() -> Connection:
    # Use a connection pool in a real-world scenario
    return sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic model for Click
class Click(BaseModel):
    id: int
    timestamp: datetime

# Endpoint to register a click
@app.post("/click", status_code=201)
async def register_click():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.utcnow()
        cursor.execute("INSERT INTO clicks (timestamp) VALUES (?)", (timestamp,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return JSONResponse(status_code=201, content={"message": "Click registered successfully"})

# Endpoint to retrieve clicks
@app.get("/clicks", response_model=list[Click])
async def retrieve_clicks(date: str = Query(..., description="The date to filter clicks.", example="2022-01-01"),
                          direction: str = Query(..., description="Specify '<', '<=' or '>' etc. to filter clicks before, before or at or after the date.", enum=["<", ">", "<=", ">="])):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        cursor.execute(query, (date_obj,))
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No clicks found")

    clicks = [Click(id=row[0], timestamp=row[1]) for row in rows]
    return clicks

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)