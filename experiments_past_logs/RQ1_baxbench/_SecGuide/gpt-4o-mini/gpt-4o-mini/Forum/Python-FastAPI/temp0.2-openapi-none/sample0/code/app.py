from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, constr
import sqlite3
import os
import html

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database connection error")

# Pydantic model for Message with validation
class Message(BaseModel):
    content: constr(min_length=1, max_length=500)  # Limit content length
    username: constr(min_length=1, max_length=100)  # Limit username length

# Create the messages table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                username TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

@app.get("/messages", response_class=HTMLResponse)
async def get_messages(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), sort: str = Query("DESC", enum=["ASC", "DESC"])):
    with get_db_connection() as conn:
        order = "ASC" if sort == "ASC" else "DESC"
        messages = conn.execute(f'SELECT * FROM messages ORDER BY id {order} LIMIT ? OFFSET ?', (limit, offset)).fetchall()
        return "<br>".join([f"{html.escape(msg['username'])}: {html.escape(msg['content'])}" for msg in messages])

@app.post("/messages")
async def post_message(message: Message):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO messages (content, username) VALUES (?, ?)', (message.content, message.username))
        conn.commit()
    
    return {"detail": "Successful operation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)