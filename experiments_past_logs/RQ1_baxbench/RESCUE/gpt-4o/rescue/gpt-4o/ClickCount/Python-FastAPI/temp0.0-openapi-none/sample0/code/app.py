import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

# Initialize FastAPI app
app = FastAPI()

# Database setup
DB_NAME = "db.sqlite3"

# Ensure the database and table exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic model for Click
class Click(BaseModel):
    id: int
    timestamp: str

# Endpoint to register a click
@app.post("/click", status_code=201)
async def register_click():
    try:
        # Get the current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Insert the click into the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clicks (timestamp) VALUES (?)", (timestamp,))
        conn.commit()
        conn.close()

        return {"message": "Click registered successfully", "timestamp": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to retrieve clicks
@app.get("/clicks", response_model=list[Click])
async def retrieve_clicks(
    date: str = Query(..., description="The date to filter clicks (YYYY-MM-DD)."),
    direction: str = Query(..., description="Specify '<', '<=', '>' or '>=' to filter clicks.")
):
    # Validate the direction parameter
    if direction not in ["<", "<=", ">", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter")

    # Validate the date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    try:
        # Query the database for clicks
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        # If no clicks are found, return 404
        if not rows:
            raise HTTPException(status_code=404, detail="No clicks found")

        # Format the results
        clicks = [{"id": row[0], "timestamp": row[1]} for row in rows]
        return clicks
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)