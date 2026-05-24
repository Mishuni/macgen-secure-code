from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
import sqlite3
import os

app = FastAPI()

DATABASE = 'db.sqlite3'

# Pydantic model for Message
class Message(BaseModel):
    content: constr(min_length=1)  # Ensure content is not empty
    username: constr(min_length=1)  # Ensure username is not empty

# Initialize the SQLite database
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

# Get all messages with optional parameters
@app.get("/messages", response_class=str)
async def get_messages(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), sort: str = Query("DESC", enum=["ASC", "DESC"])):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        order = "ASC" if sort == "ASC" else "DESC"
        cursor.execute(f'SELECT content, username FROM messages ORDER BY id {order} LIMIT ? OFFSET ?', (limit, offset))
        messages = cursor.fetchall()
        return "<br>".join([f"{username}: {content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}" for content, username in messages])

# Post a new message
@app.post("/messages")
async def post_message(message: Message):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, username) VALUES (?, ?)', (message.content, message.username))
        conn.commit()
    return {"message": "Message posted successfully"}

# Initialize the database
init_db()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)