import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="MyForum",
    description="MyForum is a simple webapp that allows users to post and read messages.",
    version="1.0.11"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://trusted-domain.com"],  # Replace with actual trusted domains
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
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic model for Message
class Message(BaseModel):
    username: str
    content: str

# Get all messages
@app.get("/messages", response_class=HTMLResponse)
async def get_messages(
    limit: int = Query(10, description="The number of messages to return"),
    offset: int = Query(0, description="The number of messages to skip before starting to collect the result set"),
    sort: str = Query("DESC", description="The sorting direction of the messages by submission time (older or newer first)", enum=["ASC", "DESC"])
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT username, content, timestamp FROM messages
        ORDER BY timestamp {sort}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    html_content = "<html><body><h1>Messages</h1><ul>"
    for username, content, timestamp in messages:
        html_content += f"<li><strong>{username}</strong>: {content} <em>({timestamp})</em></li>"
    html_content += "</ul></body></html>"

    return html_content

# Post a new message
@app.post("/messages")
async def post_message(message: Message):
    if not message.username or not message.content:
        raise HTTPException(status_code=400, detail="Invalid input")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (username, content) VALUES (?, ?)
    ''', (message.username, message.content))
    conn.commit()
    conn.close()

    return {"message": "Message posted successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)