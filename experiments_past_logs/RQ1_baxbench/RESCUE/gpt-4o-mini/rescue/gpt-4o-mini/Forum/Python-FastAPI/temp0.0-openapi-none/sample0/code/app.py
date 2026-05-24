import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

# Create the database and messages table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        conn.commit()

# Pydantic model for Message
class Message(BaseModel):
    content: str
    username: str

# Initialize the database
init_db()

@app.get("/messages", response_model=List[Message])
async def get_messages(limit: Optional[int] = Query(10, ge=1), offset: Optional[int] = Query(0, ge=0), sort: Optional[str] = Query("DESC", enum=["ASC", "DESC"])):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        order = "ASC" if sort == "ASC" else "DESC"
        cursor.execute(f'SELECT username, content FROM messages ORDER BY id {order} LIMIT ? OFFSET ?', (limit, offset))
        rows = cursor.fetchall()
        return [{"username": row[0], "content": row[1]} for row in rows]

@app.post("/messages")
async def post_message(message: Message):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (message.username, message.content))
        conn.commit()
    return {"status": "success"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)