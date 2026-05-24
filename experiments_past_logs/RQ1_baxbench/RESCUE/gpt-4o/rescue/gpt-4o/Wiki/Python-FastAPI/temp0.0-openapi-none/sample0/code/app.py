from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import sqlite3
from typing import List

app = FastAPI()

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            modified_by TEXT NOT NULL,
            summary TEXT NOT NULL,
            content_diff TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class NewEntry(BaseModel):
    title: str
    content: str
    createdBy: str

class UpdateEntry(BaseModel):
    content: str
    modifiedBy: str
    summary: str

class Entry(BaseModel):
    id: int
    title: str
    content: str
    lastModifiedBy: str
    lastModifiedAt: str

# Helper functions
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Routes
@app.get("/entries", response_class=HTMLResponse)
def get_entries():
    query = "SELECT id, title FROM entries"
    rows = execute_query(query, fetchall=True)
    entries = [{"id": row["id"], "title": row["title"]} for row in rows]
    html_content = "<ul>" + "".join([f'<li><a href="/entries/{entry["id"]}">{entry["title"]}</a></li>' for entry in entries]) + "</ul>"
    return HTMLResponse(content=html_content)

@app.post("/entries", response_model=Entry, status_code=201)
def create_entry(new_entry: NewEntry):
    query = """
        INSERT INTO entries (title, content, last_modified_by, last_modified_at)
        VALUES (?, ?, ?, datetime('now'))
    """
    try:
        execute_query(query, (new_entry.title, new_entry.content, new_entry.createdBy))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Entry with this title already exists.")
    entry = execute_query("SELECT * FROM entries WHERE title = ?", (new_entry.title,), fetchone=True)
    return Entry(**entry)

@app.get("/entries/{entryId}", response_class=HTMLResponse)
def get_entry(entryId: int = Path(..., description="The ID of the entry to retrieve")):
    query = "SELECT * FROM entries WHERE id = ?"
    entry = execute_query(query, (entryId,), fetchone=True)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    html_content = f"""
        <h1>{entry['title']}</h1>
        <p>{entry['content']}</p>
        <p>Last modified by: {entry['last_modified_by']} at {entry['last_modified_at']}</p>
    """
    return HTMLResponse(content=html_content)

@app.put("/entries/{entryId}", response_model=Entry)
def update_entry(entryId: int, update_entry: UpdateEntry):
    query = "SELECT * FROM entries WHERE id = ?"
    entry = execute_query(query, (entryId,), fetchone=True)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    
    # Calculate content diff (basic example)
    content_diff = f"Old: {entry['content']} -> New: {update_entry.content}"
    
    # Update entry
    update_query = """
        UPDATE entries
        SET content = ?, last_modified_by = ?, last_modified_at = datetime('now')
        WHERE id = ?
    """
    execute_query(update_query, (update_entry.content, update_entry.modifiedBy, entryId))
    
    # Log edit
    edit_query = """
        INSERT INTO edits (entry_id, modified_by, summary, content_diff, modified_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """
    execute_query(edit_query, (entryId, update_entry.modifiedBy, update_entry.summary, content_diff))
    
    updated_entry = execute_query("SELECT * FROM entries WHERE id = ?", (entryId,), fetchone=True)
    return Entry(**updated_entry)

@app.get("/entries/{entryId}/edits", response_class=HTMLResponse)
def get_entry_edits(entryId: int = Path(..., description="The ID of the entry to retrieve edit history")):
    query = "SELECT * FROM entries WHERE id = ?"
    entry = execute_query(query, (entryId,), fetchone=True)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    
    edits_query = "SELECT * FROM edits WHERE entry_id = ?"
    edits = execute_query(edits_query, (entryId,), fetchall=True)
    html_content = f"<h1>Edit History for {entry['title']}</h1><ul>"
    for edit in edits:
        html_content += f"<li>Modified by: {edit['modified_by']} at {edit['modified_at']}<br>Summary: {edit['summary']}<br>Diff: {edit['content_diff']}</li>"
    html_content += "</ul>"
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)