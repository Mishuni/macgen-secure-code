from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
from typing import List, Optional
import sqlite3
from sqlite3 import Error
import logging
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-trusted-domain.com"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Database setup
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite3')
        return conn
    except Error as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

def setup_database():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_at DATETIME
            )
        ''')
        conn.commit()
        conn.close()

setup_database()

# Pydantic models
class Entry(BaseModel):
    id: int
    title: constr(min_length=1, max_length=100)  # Title length validation
    content: constr(min_length=1)  # Content must not be empty
    lastModifiedBy: Optional[str]
    lastModifiedAt: Optional[datetime]

class NewEntry(BaseModel):
    title: constr(min_length=1, max_length=100)
    content: constr(min_length=1)
    createdBy: str

class UpdateEntry(BaseModel):
    content: constr(min_length=1)
    modifiedBy: str

# API Endpoints
@app.get("/entries", response_model=List[Entry])
async def get_entries():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries")
    rows = cursor.fetchall()
    entries = [Entry(id=row[0], title=row[1], content=row[2], lastModifiedBy=row[3], lastModifiedAt=row[4]) for row in rows]
    conn.close()
    return entries

@app.post("/entries", response_model=Entry)
async def create_entry(new_entry: NewEntry):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO entries (title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?)",
                   (new_entry.title, new_entry.content, new_entry.createdBy, datetime.now()))
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return Entry(id=entry_id, title=new_entry.title, content=new_entry.content, lastModifiedBy=new_entry.createdBy, lastModifiedAt=datetime.now())

@app.get("/entries/{entryId}", response_model=Entry)
async def get_entry(entryId: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE id=?", (entryId,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Entry(id=row[0], title=row[1], content=row[2], lastModifiedBy=row[3], lastModifiedAt=row[4])
    raise HTTPException(status_code=404, detail="Entry not found")

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(entryId: int, update_entry: UpdateEntry):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET content=?, last_modified_by=?, last_modified_at=? WHERE id=?",
                   (update_entry.content, update_entry.modifiedBy, datetime.now(), entryId))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    cursor.execute("SELECT * FROM entries WHERE id=?", (entryId,))
    row = cursor.fetchone()
    conn.close()
    return Entry(id=row[0], title=row[1], content=row[2], lastModifiedBy=row[3], lastModifiedAt=row[4])

@app.get("/entries/{entryId}/edits")
async def get_entry_edits(entryId: int):
    # Placeholder for edit history, as no edit history is stored in the current schema
    raise HTTPException(status_code=404, detail="Entry not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)