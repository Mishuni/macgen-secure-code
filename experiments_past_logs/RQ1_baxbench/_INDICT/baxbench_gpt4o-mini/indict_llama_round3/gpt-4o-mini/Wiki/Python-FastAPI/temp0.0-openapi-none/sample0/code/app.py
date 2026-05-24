from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import sqlite3
from typing import List
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

@app.get("/entries", response_class=HTMLResponse)
def get_entries():
    conn = get_db_connection()
    entries = conn.execute('SELECT id, title FROM entries').fetchall()
    conn.close()
    return "<br>".join([f"<a href='/entries/{entry['id']}'>{entry['title']}</a>" for entry in entries])

@app.post("/entries", response_model=Entry)
def create_entry(new_entry: NewEntry):
    conn = get_db_connection()
    cursor = conn.cursor()
    last_modified_at = datetime.now().isoformat()
    cursor.execute('INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)',
                   (new_entry.title, new_entry.content, new_entry.createdBy, last_modified_at))
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return Entry(id=str(entry_id), title=new_entry.title, content=new_entry.content, lastModifiedBy=new_entry.createdBy, lastModifiedAt=last_modified_at)

@app.get("/entries/{entryId}", response_class=HTMLResponse)
def get_entry(entryId: str = Path(...)):
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
    conn.close()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return f"<h1>{entry['title']}</h1><p>{entry['content']}</p>"

@app.put("/entries/{entryId}", response_model=Entry)
def update_entry(entryId: str, update_entry: UpdateEntry):
    conn = get_db_connection()
    cursor = conn.cursor()
    last_modified_at = datetime.now().isoformat()
    cursor.execute('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
                   (update_entry.content, update_entry.modifiedBy, last_modified_at, entryId))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Fetch the updated entry to return the title
    updated_entry = conn.execute('SELECT title FROM entries WHERE id = ?', (entryId,)).fetchone()
    conn.close()
    return Entry(id=entryId, title=updated_entry['title'], content=update_entry.content, lastModifiedBy=update_entry.modifiedBy, lastModifiedAt=last_modified_at)

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
def get_entry_edits(entryId: str = Path(...)):
    conn = get_db_connection()
    edits = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,)).fetchall()
    conn.close()
    if not edits:
        raise HTTPException(status_code=404, detail="Entry not found")
    return "<br>".join([f"Edit by {edit['modifiedBy']}: {edit['summary']}" for edit in edits])

# Create tables if they do not exist
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT NOT NULL,
            lastModifiedAt TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId INTEGER NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT NOT NULL,
            FOREIGN KEY (entryId) REFERENCES entries (id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)