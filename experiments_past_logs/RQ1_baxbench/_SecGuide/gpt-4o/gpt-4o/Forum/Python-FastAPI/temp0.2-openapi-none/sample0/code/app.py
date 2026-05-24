import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, constr
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import html
from contextlib import contextmanager
from sqlite3 import Error

# Initialize FastAPI app
app = FastAPI(title="MyForum", description="MyForum is a simple webapp that allows users to post and read messages.", version="1.0.11")

# Set up CORS middleware with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # Replace with your allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Database setup
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

# Context manager for database connections
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Pydantic model for Message with validation
class Message(BaseModel):
    username: constr(min_length=1, max_length=50)
    content: constr(min_length=1, max_length=500)

# Endpoint to get all messages
@app.get("/messages", response_class=HTMLResponse)
async def get_messages(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), sort: str = Query("DESC", regex="^(ASC|DESC)$")):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, content, timestamp FROM messages
                ORDER BY timestamp {}
                LIMIT ? OFFSET ?
            '''.format(sort), (limit, offset))
            messages = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail="Database error")

    # Construct HTML response
    html_content = "<html><body><h1>Messages</h1><ul>"
    for username, content, timestamp in messages:
        html_content += f"<li><strong>{html.escape(username)}</strong>: {html.escape(content)} <em>at {timestamp}</em></li>"
    html_content += "</ul></body></html>"

    return HTMLResponse(content=html_content, media_type="text/html")

# Endpoint to post a new message
@app.post("/messages", response_class=JSONResponse)
async def post_message(message: Message):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (username, content) VALUES (?, ?)
            ''', (message.username, message.content))
            conn.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail="Database error")

    return JSONResponse(content={"message": "Message posted successfully"}, status_code=200)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)