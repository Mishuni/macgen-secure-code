import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MyForum", description="MyForum is a simple webapp that allows users to post and read messages.", version="1.0.11")

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Pydantic model for Message
class Message(BaseModel):
    content: str
    username: str

# GET /messages endpoint
@app.get("/messages", response_class=HTMLResponse)
async def get_messages(limit: int = 10, offset: int = 0, sort: str = "desc"):
    if sort.lower() not in ["asc", "desc"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sort parameter")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT * FROM messages
        ORDER BY created_at {sort.upper()}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()
    conn.close()

    html_content = "<html><body><h1>Messages</h1><ul>"
    for message in messages:
        html_content += f"<li><strong>{message['username']}</strong>: {message['content']} (Posted on {message['created_at']})</li>"
    html_content += "</ul></body></html>"
    return HTMLResponse(content=html_content)

# POST /messages endpoint
@app.post("/messages", status_code=status.HTTP_200_OK)
async def post_message(message: Message):
    if not message.content or not message.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (content, username) VALUES (?, ?)
    ''', (message.content, message.username))
    conn.commit()
    conn.close()
    return {"message": "Message posted successfully"}

# Start the web server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)