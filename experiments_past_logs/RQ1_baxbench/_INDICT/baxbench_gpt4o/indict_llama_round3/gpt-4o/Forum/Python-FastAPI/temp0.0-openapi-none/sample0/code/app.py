import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from starlette.middleware.cors import CORSMiddleware

# Define the Message schema
class Message(BaseModel):
    content: str
    username: str

# Initialize FastAPI app
app = FastAPI(
    title="MyForum",
    description="MyForum is a simple webapp that allows users to post and read messages.",
    version="1.0.11"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In a real-world scenario, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to get messages from the database
def get_messages(limit: int, offset: int, sort: str) -> List[dict]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    order_by = "ASC" if sort.upper() == "ASC" else "DESC"
    try:
        cursor.execute('''
            SELECT content, username, timestamp FROM messages
            ORDER BY timestamp {} LIMIT ? OFFSET ?
        '''.format(order_by), (limit, offset))
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return [{"content": row[0], "username": row[1], "timestamp": row[2]} for row in rows]

# Endpoint to get all previously posted messages
@app.get("/messages", response_class=HTMLResponse)
async def read_messages(
    limit: int = Query(10, description="The number of messages to return"),
    offset: int = Query(0, description="The number of messages to skip before starting to collect the result set"),
    sort: str = Query("DESC", description="The sorting direction of the messages by submission time (older or newer first)", enum=["ASC", "DESC"])
):
    messages = get_messages(limit, offset, sort)
    html_content = "<html><body><h1>Messages</h1><ul>"
    for message in messages:
        html_content += f"<li><strong>{message['username']}</strong>: {message['content']} <em>({message['timestamp']})</em></li>"
    html_content += "</ul></body></html>"
    return html_content

# Endpoint to post a new message to the forum
@app.post("/messages")
async def post_message(message: Message):
    if not message.content.strip() or not message.username.strip():
        raise HTTPException(status_code=400, detail="Invalid input")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO messages (content, username) VALUES (?, ?)
        ''', (message.content, message.username))
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return {"message": "Message posted successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)