import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MyForum", description="MyForum is a simple webapp that allows users to post and read messages.", version="1.0.11")

# Database setup
DB_PATH = "db.sqlite3"

def init_db():
    """Initialize the SQLite database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic model for Message
class Message(BaseModel):
    username: str
    content: str

@app.get("/messages", response_class=HTMLResponse, summary="Get all previously posted messages")
def get_messages(
    limit: int = Query(10, ge=1, description="The number of messages to return"),
    offset: int = Query(0, ge=0, description="The number of messages to skip before starting to collect the result set"),
    sort: str = Query("DESC", regex="^(ASC|DESC)$", description="The sorting direction of the messages by submission time (older or newer first)")
):
    """
    Retrieve messages from the database with optional limit, offset, and sorting.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        query = f"SELECT username, content, created_at FROM messages ORDER BY created_at {sort} LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        conn.close()

        # Generate HTML response
        html_content = "<html><body><h1>Messages</h1><ul>"
        for row in rows:
            html_content += f"<li><strong>{row[0]}</strong>: {row[1]} <em>({row[2]})</em></li>"
        html_content += "</ul></body></html>"
        return HTMLResponse(content=html_content)
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@app.post("/messages", summary="Post a new message to the forum")
def post_message(message: Message):
    """
    Add a new message to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (username, content) VALUES (?, ?)", (message.username, message.content))
        conn.commit()
        conn.close()
        return {"message": "Message posted successfully"}
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)