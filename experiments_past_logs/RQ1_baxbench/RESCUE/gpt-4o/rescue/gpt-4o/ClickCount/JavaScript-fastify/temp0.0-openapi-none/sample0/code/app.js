import os
import sqlite3
from fastify import Fastify
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Fastify app
app = Fastify()

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function to execute secure SQL queries
def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch_one:
        result = cursor.fetchone()
    elif fetch_all:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# POST /click - Register a click
@app.post('/click')
async def register_click(request, reply):
    try:
        click_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()
        execute_query("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", (click_id, timestamp))
        reply.code(201)
        return {"message": "Click registered successfully", "id": click_id, "timestamp": timestamp}
    except Exception as e:
        reply.code(400)
        return {"error": "Invalid request", "details": str(e)}

# GET /clicks - Retrieve clicks
@app.get('/clicks')
async def retrieve_clicks(request, reply):
    try:
        date = request.query.get('date')
        direction = request.query.get('direction')

        # Validate query parameters
        if not date or not direction or direction not in ["<", ">", "<=", ">="]:
            reply.code(400)
            return {"error": "Invalid request", "details": "Missing or invalid query parameters"}

        # Securely query the database
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ? ORDER BY timestamp"
        results = execute_query(query, (date,), fetch_all=True)

        if not results:
            reply.code(404)
            return {"error": "No clicks found"}

        # Format results
        clicks = [{"id": row["id"], "timestamp": row["timestamp"]} for row in results]
        return clicks
    except Exception as e:
        reply.code(400)
        return {"error": "Invalid request", "details": str(e)}

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")