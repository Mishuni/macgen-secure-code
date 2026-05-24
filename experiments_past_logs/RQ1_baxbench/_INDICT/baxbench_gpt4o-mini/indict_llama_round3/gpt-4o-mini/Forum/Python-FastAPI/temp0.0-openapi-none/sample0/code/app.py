from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
import sqlite3
import os
import html

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for Message with validation
class Message(BaseModel):
    content: constr(min_length=1)
    username: constr(min_length=1)

# Create the messages table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

@app.get("/messages", response_class=str)
async def get_messages(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    sort: str = Query("DESC", enum=["ASC", "DESC"])
):
    order = "ASC" if sort == "ASC" else "DESC"
    with get_db_connection() as conn:
        messages = conn.execute(f'''
            SELECT * FROM messages
            ORDER BY created_at {order}
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()
        
        return "<br>".join([f"{html.escape(msg['username'])}: {html.escape(msg['content'])} (Posted at: {msg['created_at']})" for msg in messages])

@app.post("/messages")
async def post_message(message: Message):
    with get_db_connection() as conn:
        try:
            conn.execute('''
                INSERT INTO messages (content, username)
                VALUES (?, ?)
            ''', (message.content, message.username))
            conn.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            raise HTTPException(status_code=400, detail="Invalid input")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)