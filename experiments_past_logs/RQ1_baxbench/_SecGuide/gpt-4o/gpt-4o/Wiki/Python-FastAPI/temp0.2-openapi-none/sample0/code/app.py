from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
import sqlite3
from datetime import datetime
from typing import List
import html
import logging

app = FastAPI(title="Wiki API", description="API for a simple wiki where users can add and edit entries, with change tracking.", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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
    conn.close()

init_db()

# Pydantic models
class Entry(BaseModel):
    id: int
    title: str
    content: str
    lastModifiedBy: str
    lastModifiedAt: str

class NewEntry(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    createdBy: str = Field(..., min_length=1, max_length=100)

class UpdateEntry(BaseModel):
    content: str = Field(..., min_length=1)
    modifiedBy: str = Field(..., min_length=1, max_length=100)
    summary: str = Field(..., min_length=1, max_length=255)

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.get("/entries", response_class=HTMLResponse)
async def get_entries():
    try:
        conn = get_db_connection()
        entries = conn.execute('SELECT id, title FROM entries').fetchall()
        conn.close()
        html_content = "<h1>Wiki Entries</h1><ul>"
        for entry in entries:
            html_content += f'<li><a href="/entries/{entry["id"]}">{html.escape(entry["title"])}</a></li>'
        html_content += "</ul>"
        return html_content
    except Exception as e:
        logger.error(f"Error retrieving entries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/entries", response_model=Entry, status_code=201)
async def create_entry(new_entry: NewEntry):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
            VALUES (?, ?, ?, ?)
        ''', (new_entry.title, new_entry.content, new_entry.createdBy, datetime.utcnow().isoformat()))
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return Entry(id=entry_id, title=new_entry.title, content=new_entry.content, lastModifiedBy=new_entry.createdBy, lastModifiedAt=datetime.utcnow().isoformat())
    except Exception as e:
        logger.error(f"Error creating entry: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/entries/{entryId}", response_class=HTMLResponse)
async def get_entry(entryId: int = Path(..., description="The ID of the entry to retrieve")):
    try:
        conn = get_db_connection()
        entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
        conn.close()
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        html_content = f"<h1>{html.escape(entry['title'])}</h1><p>{html.escape(entry['content'])}</p><p>Last modified by: {html.escape(entry['lastModifiedBy'])} at {entry['lastModifiedAt']}</p>"
        return html_content
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving entry: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(entryId: int, update_entry: UpdateEntry):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        entry = cursor.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
        if entry is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found")
        cursor.execute('''
            UPDATE entries
            SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
            WHERE id = ?
        ''', (update_entry.content, update_entry.modifiedBy, datetime.utcnow().isoformat(), entryId))
        cursor.execute('''
            INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (entryId, update_entry.content, update_entry.modifiedBy, update_entry.summary, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return Entry(id=entryId, title=entry['title'], content=update_entry.content, lastModifiedBy=update_entry.modifiedBy, lastModifiedAt=datetime.utcnow().isoformat())
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating entry: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
async def get_entry_edits(entryId: int = Path(..., description="The ID of the entry to retrieve edit history for")):
    try:
        conn = get_db_connection()
        edits = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,)).fetchall()
        conn.close()
        if not edits:
            raise HTTPException(status_code=404, detail="Entry not found")
        html_content = "<h1>Edit History</h1><ul>"
        for edit in edits:
            html_content += f'<li>Modified by: {html.escape(edit["modifiedBy"])} at {edit["modifiedAt"]} - Summary: {html.escape(edit["summary"])}</li>'
        html_content += "</ul>"
        return html_content
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving edit history: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)