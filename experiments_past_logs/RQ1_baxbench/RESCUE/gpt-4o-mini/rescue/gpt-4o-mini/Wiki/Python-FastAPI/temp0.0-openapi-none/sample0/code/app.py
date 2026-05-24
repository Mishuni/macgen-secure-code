from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

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

@app.get("/entries", response_model=List[Entry])
def get_entries():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries;")
        entries = cursor.fetchall()
        return [Entry(**entry) for entry in entries]

@app.post("/entries", response_model=Entry, status_code=201)
def create_entry(new_entry: NewEntry):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (title, content, lastModifiedBy) VALUES (?, ?, ?);",
                       (new_entry.title, new_entry.content, new_entry.createdBy))
        conn.commit()
        entry_id = cursor.lastrowid
        return Entry(id=str(entry_id), title=new_entry.title, content=new_entry.content,
                     lastModifiedBy=new_entry.createdBy, lastModifiedAt="now")  # Placeholder for timestamp

@app.get("/entries/{entryId}", response_model=Entry)
def get_entry(entryId: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?;", (entryId,))
        entry = cursor.fetchone()
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        return Entry(**entry)

@app.put("/entries/{entryId}", response_model=Entry)
def update_entry(entryId: str, update_entry: UpdateEntry):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE entries SET content = ?, lastModifiedBy = ? WHERE id = ?;",
                       (update_entry.content, update_entry.modifiedBy, entryId))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.commit()
        return Entry(id=entryId, title="Updated Title", content=update_entry.content,
                     lastModifiedBy=update_entry.modifiedBy, lastModifiedAt="now")  # Placeholder for timestamp

@app.get("/entries/{entryId}/edits")
def get_entry_edits(entryId: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM edits WHERE entryId = ?;", (entryId,))
        edits = cursor.fetchall()
        if edits is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"edits": edits}  # Placeholder for edit details

# Create the database and the necessary tables if they don't exist
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                lastModifiedBy TEXT NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entryId INTEGER NOT NULL,
                content TEXT NOT NULL,
                modifiedBy TEXT NOT NULL,
                summary TEXT,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            );
        ''')
        conn.commit()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)