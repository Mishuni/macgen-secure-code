import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = "db.sqlite3"

# Ensure the database and table are created
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Data model for Click
class Click(BaseModel):
    id: int
    timestamp: datetime

# POST /click endpoint to register a click
@app.post("/click", status_code=201)
async def register_click():
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clicks (timestamp) VALUES (CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
        return JSONResponse(status_code=201, content={"message": "Click registered successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request")

# GET /clicks endpoint to retrieve clicks
@app.get("/clicks", response_model=list[Click])
async def retrieve_clicks(
    date: str = Query(..., description="The date to filter clicks.", example="2022-01-01"),
    direction: str = Query(..., description="Specify '<', '<=' or '>' etc. to filter clicks.", enum=["<", ">", "<=", ">="])
):
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            raise HTTPException(status_code=404, detail="No clicks found")

        clicks = [Click(id=row[0], timestamp=row[1]) for row in rows]
        return clicks
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)