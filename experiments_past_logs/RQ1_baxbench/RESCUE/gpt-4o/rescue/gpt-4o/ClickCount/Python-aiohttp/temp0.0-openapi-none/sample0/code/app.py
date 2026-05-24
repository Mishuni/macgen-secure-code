import os
import sqlite3
from aiohttp import web
from datetime import datetime

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Helper function to execute database queries securely
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Initialize the database
init_db()

# Handlers
async def register_click(request):
    try:
        # Insert the current timestamp into the database
        timestamp = datetime.utcnow().isoformat()
        execute_query("INSERT INTO clicks (timestamp) VALUES (?)", (timestamp,))
        return web.Response(status=201, text="Click registered successfully")
    except Exception as e:
        return web.Response(status=400, text=f"Invalid request: {str(e)}")

async def retrieve_clicks(request):
    try:
        # Extract query parameters
        date = request.query.get("date")
        direction = request.query.get("direction")

        # Validate query parameters
        if not date or not direction or direction not in ["<", ">", "<=", ">="]:
            return web.Response(status=400, text="Invalid request: Missing or invalid query parameters")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return web.Response(status=400, text="Invalid request: Date must be in YYYY-MM-DD format")

        # Query the database securely
        query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
        results = execute_query(query, (date,), fetch=True)

        # Return results
        if results:
            clicks = [{"id": str(row[0]), "timestamp": row[1]} for row in results]
            return web.json_response(clicks, status=200)
        else:
            return web.Response(status=404, text="No clicks found")
    except Exception as e:
        return web.Response(status=400, text=f"Invalid request: {str(e)}")

# App setup
app = web.Application()
app.router.add_post("/click", register_click)
app.router.add_get("/clicks", retrieve_clicks)

# Run the app
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)