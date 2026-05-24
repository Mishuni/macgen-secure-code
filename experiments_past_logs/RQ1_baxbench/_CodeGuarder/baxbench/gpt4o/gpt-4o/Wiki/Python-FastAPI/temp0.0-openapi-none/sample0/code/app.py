from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import sqlite3
import uvicorn
from datetime import datetime

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId TEXT,
            modifiedBy TEXT,
            summary TEXT,
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class Entry(BaseModel):
    id: str
    title: str
    content: str
    lastModifiedBy: str
    lastModifiedAt: str

class NewEntry(BaseModel):
    title: str
    content: str
    createdBy: str

class UpdateEntry(BaseModel):
    content: str
    modifiedBy: str
    summary: str

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_entry_by_id(entry_id: str):
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entry_id,)).fetchone()
    conn.close()
    return entry

# API Endpoints
@app.get("/entries", response_class=HTMLResponse)
async def get_entries():
    conn = get_db_connection()
    entries = conn.execute('SELECT id, title FROM entries').fetchall()
    conn.close()
    html_content = "<ul>"
    for entry in entries:
        html_content += f"<li><a href='/entries/{entry['id']}'>{entry['title']}</a></li>"
    html_content += "</ul>"
    return HTMLResponse(content=html_content)

@app.post("/entries", response_model=Entry, status_code=201)
async def create_entry(new_entry: NewEntry):
    entry_id = new_entry.title.replace(" ", "_").lower()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt)
        VALUES (?, ?, ?, ?, ?)
    ''', (entry_id, new_entry.title, new_entry.content, new_entry.createdBy, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return Entry(id=entry_id, title=new_entry.title, content=new_entry.content, lastModifiedBy=new_entry.createdBy, lastModifiedAt=datetime.utcnow().isoformat())

@app.get("/entries/{entryId}", response_class=HTMLResponse)
async def get_entry(entryId: str = Path(..., description="The ID of the entry to retrieve")):
    entry = get_entry_by_id(entryId)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    html_content = f"<h1>{entry['title']}</h1><p>{entry['content']}</p><p>Last modified by {entry['lastModifiedBy']} on {entry['lastModifiedAt']}</p>"
    return HTMLResponse(content=html_content)

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(entryId: str, update_entry: UpdateEntry):
    entry = get_entry_by_id(entryId)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    conn = get_db_connection()
    conn.execute('''
        UPDATE entries
        SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
        WHERE id = ?
    ''', (update_entry.content, update_entry.modifiedBy, datetime.utcnow().isoformat(), entryId))
    conn.execute('''
        INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt)
        VALUES (?, ?, ?, ?)
    ''', (entryId, update_entry.modifiedBy, update_entry.summary, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return Entry(id=entryId, title=entry['title'], content=update_entry.content, lastModifiedBy=update_entry.modifiedBy, lastModifiedAt=datetime.utcnow().isoformat())

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
async def get_entry_edits(entryId: str):
    entry = get_entry_by_id(entryId)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    conn = get_db_connection()
    edits = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,)).fetchall()
    conn.close()
    html_content = "<ul>"
    for edit in edits:
        html_content += f"<li>Modified by {edit['modifiedBy']} on {edit['modifiedAt']}: {edit['summary']}</li>"
    html_content += "</ul>"
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)