import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET")

# Initialize FastAPI application
app = FastAPI(title="MyForum", description="MyForum is a simple webapp that allows users to post and read messages.", version="1.0.11")

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                username TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Pydantic model for message schema
class Message(BaseModel):
    content: str
    username: str

# GET endpoint to retrieve messages
@app.get("/messages", response_model=List[Message])
async def get_messages(limit: Optional[int] = 10, offset: Optional[int] = 0, sort: Optional[str] = "DESC"):
    if sort not in ["ASC", "DESC"]:
        raise HTTPException(status_code=400, detail="Invalid sort parameter. Use 'ASC' or 'DESC'.")
    
    order = "ASC" if sort == "ASC" else "DESC"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT content, username FROM messages ORDER BY id {order} LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
    
    return [Message(content=row[0], username=row[1]) for row in rows]

# POST endpoint to post a new message
@app.post("/messages", response_model=Message)
async def post_message(message: Message):
    if not message.content or not message.username:
        raise HTTPException(status_code=400, detail="Content and username are required.")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (content, username) VALUES (?, ?)", (message.content, message.username))
        conn.commit()
    
    return message

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)