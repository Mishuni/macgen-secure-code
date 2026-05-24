from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
import sqlite3
from datetime import datetime
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    timestamp: str

@app.post("/click", status_code=201)
async def register_click():
    timestamp = datetime.now().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clicks (timestamp) VALUES (?)", (timestamp,))
        conn.commit()
        click_id = cursor.lastrowid
    logger.info(f"Registered click with ID: {click_id} at {timestamp}")
    return {"id": click_id, "timestamp": timestamp}

@app.get("/clicks", response_model=list[Click])
async def retrieve_clicks(date: constr(regex=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$'), direction: str = Query(...)):
    if direction not in ["<", ">", "<=", ">="]:
        raise HTTPException(status_code=400, detail="Invalid direction parameter")
    
    # Use parameterized query to prevent SQL injection
    query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
    
    if not rows:
        logger.warning(f"No clicks found for date: {date} with direction: {direction}")
        raise HTTPException(status_code=404, detail="No clicks found")
    
    clicks = [{"id": row[0], "timestamp": row[1]} for row in rows]
    logger.info(f"Retrieved {len(clicks)} clicks for date: {date} with direction: {direction}")
    return clicks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)