import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Initialize FastAPI
app = FastAPI()

# Database setup
DB_FILE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                last_modified_by TEXT NOT NULL,
                last_modified_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                summary TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Pydantic models
class Entry(BaseModel):
    id: str
    title: str
    content: str
    last_modified_by: str
    last_modified_at: str

class NewEntry(BaseModel):
    title: str
    content: str
    createdBy: str

class UpdateEntry(BaseModel):
    content: str
    modifiedBy: str
    summary: str

# API Endpoints
@app.get("/entries", response_class=HTMLResponse)
async def get_entries():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM entries")
        entries = cursor.fetchall()
        return "<br>".join([f"<a href='/entries/{entry[0]}'>{entry[1]}</a>" for entry in entries])

@app.post("/entries", response_model=Entry)
async def create_entry(entry: NewEntry):
    entry_id = str(datetime.now().timestamp())
    last_modified_at = datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)",
                       (entry_id, entry.title, entry.content, entry.createdBy, last_modified_at))
        conn.commit()
    return Entry(id=entry_id, title=entry.title, content=entry.content, last_modified_by=entry.createdBy, last_modified_at=last_modified_at)

@app.get("/entries/{entryId}", response_class=HTMLResponse)
async def get_entry(entryId: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entryId,))
        entry = cursor.fetchone()
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        return f"<h1>{entry[1]}</h1><p>{entry[2]}</p>"

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(entryId: str, entry: UpdateEntry):
    last_modified_at = datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
                       (entry.content, entry.modifiedBy, last_modified_at, entryId))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        cursor.execute("INSERT INTO edits (entry_id, modified_by, summary, modified_at) VALUES (?, ?, ?, ?)",
                       (entryId, entry.modifiedBy, entry.summary, last_modified_at))
        conn.commit()
    return Entry(id=entryId, title="", content=entry.content, last_modified_by=entry.modifiedBy, last_modified_at=last_modified_at)

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
async def get_entry_edits(entryId: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM edits WHERE entry_id = ?", (entryId,))
        edits = cursor.fetchall()
        if not edits:
            raise HTTPException(status_code=404, detail="Entry not found")
        return "<br>".join([f"Edited by {edit[2]}: {edit[3]} at {edit[4]}" for edit in edits])

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)