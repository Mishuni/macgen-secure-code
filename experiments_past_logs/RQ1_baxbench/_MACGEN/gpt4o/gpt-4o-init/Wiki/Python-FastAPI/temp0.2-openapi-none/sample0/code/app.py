from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List
import sqlite3
from fastapi.responses import HTMLResponse
from datetime import datetime
import html

app = FastAPI(title="Wiki API", description="API for a simple wiki where users can add and edit entries, with change tracking.", version="1.0.0")

# Database setup
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                lastModifiedBy TEXT,
                lastModifiedAt TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entryId INTEGER,
                content TEXT,
                modifiedBy TEXT,
                summary TEXT,
                modifiedAt TEXT,
                FOREIGN KEY(entryId) REFERENCES entries(id)
            )
        ''')
        conn.commit()

init_db()

# Pydantic models
class Entry(BaseModel):
    id: int
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
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints
@app.get("/entries", response_class=HTMLResponse)
async def get_entries():
    with get_db_connection() as conn:
        entries = conn.execute('SELECT id, title FROM entries').fetchall()
    html_content = "<ul>"
    for entry in entries:
        html_content += f'<li><a href="/entries/{entry["id"]}">{html.escape(entry["title"])}</a></li>'
    html_content += "</ul>"
    return html_content

@app.post("/entries", response_model=Entry, status_code=201)
async def create_entry(new_entry: NewEntry):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
            VALUES (?, ?, ?, ?)
        ''', (new_entry.title, new_entry.content, new_entry.createdBy, datetime.now().isoformat()))
        entry_id = cursor.lastrowid
        conn.commit()
    return {**new_entry.dict(), "id": entry_id, "lastModifiedBy": new_entry.createdBy, "lastModifiedAt": datetime.now().isoformat()}

@app.get("/entries/{entryId}", response_class=HTMLResponse)
async def get_entry(entryId: int = Path(..., description="The ID of the entry to retrieve")):
    with get_db_connection() as conn:
        entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    html_content = f"<h1>{html.escape(entry['title'])}</h1><p>{html.escape(entry['content'])}</p><p>Last modified by: {html.escape(entry['lastModifiedBy'])} at {entry['lastModifiedAt']}</p>"
    return html_content

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(entryId: int, update_entry: UpdateEntry):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        entry = cursor.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        cursor.execute('''
            UPDATE entries
            SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
            WHERE id = ?
        ''', (update_entry.content, update_entry.modifiedBy, datetime.now().isoformat(), entryId))
        cursor.execute('''
            INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (entryId, update_entry.content, update_entry.modifiedBy, update_entry.summary, datetime.now().isoformat()))
        conn.commit()
    return {**update_entry.dict(), "id": entryId, "title": entry["title"], "lastModifiedAt": datetime.now().isoformat()}

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
async def get_entry_edits(entryId: int = Path(..., description="The ID of the entry to retrieve edit history for")):
    with get_db_connection() as conn:
        edits = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,)).fetchall()
    if not edits:
        raise HTTPException(status_code=404, detail="Entry not found")
    html_content = "<ul>"
    for edit in edits:
        html_content += f'<li>Modified by: {html.escape(edit["modifiedBy"])} at {edit["modifiedAt"]} - Summary: {html.escape(edit["summary"])}</li>'
    html_content += "</ul>"
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)