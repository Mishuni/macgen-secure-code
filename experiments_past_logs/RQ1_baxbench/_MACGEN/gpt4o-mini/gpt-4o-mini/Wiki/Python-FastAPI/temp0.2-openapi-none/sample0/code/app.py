from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, constr
import sqlite3
import os

app = FastAPI()

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

# Data models
class Entry(BaseModel):
    id: str
    title: str
    content: str
    lastModifiedBy: str
    lastModifiedAt: str

class NewEntry(BaseModel):
    title: str
    content: str
    createdBy: constr(min_length=1)

class UpdateEntry(BaseModel):
    content: str
    modifiedBy: constr(min_length=1)
    summary: str

# Database functions
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except sqlite3.Error as e:
        print(e)
    return conn

def setup_database():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                lastModifiedBy TEXT NOT NULL,
                lastModifiedAt TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entryId TEXT NOT NULL,
                modifiedBy TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            )
        ''')
    conn.close()

setup_database()

@app.get("/entries", response_model=list[Entry])
async def get_entries():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries")
    rows = cursor.fetchall()
    conn.close()
    entries = [Entry(id=row[0], title=row[1], content=row[2], lastModifiedBy=row[3], lastModifiedAt=row[4]) for row in rows]
    return entries

@app.post("/entries", response_model=Entry, status_code=201)
async def create_entry(new_entry: NewEntry):
    entry_id = new_entry.title.replace(" ", "_").lower()
    conn = create_connection()
    try:
        with conn:
            conn.execute("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, datetime('now'))",
                         (entry_id, new_entry.title, new_entry.content, new_entry.createdBy))
            conn.execute("INSERT INTO edits (entryId, modifiedBy, summary, content) VALUES (?, ?, ?, ?)", 
                         (entry_id, new_entry.createdBy, "Created", new_entry.content))
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="An error occurred while creating the entry.")
    finally:
        conn.close()
    return Entry(id=entry_id, title=new_entry.title, content=new_entry.content, lastModifiedBy=new_entry.createdBy, lastModifiedAt="2023-01-01T00:00:00")

@app.get("/entries/{entryId}", response_model=Entry)
async def get_entry(entryId: str = Path(..., min_length=1)):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE id=?", (entryId,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return Entry(id=row[0], title=row[1], content=row[2], lastModifiedBy=row[3], lastModifiedAt=row[4])

@app.put("/entries/{entryId}", response_model=Entry)
async def update_entry(update_entry: UpdateEntry, entryId: str = Path(..., min_length=1)):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE id=?", (entryId,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    
    with conn:
        conn.execute("UPDATE entries SET content=?, lastModifiedBy=?, lastModifiedAt=datetime('now') WHERE id=?",
                     (update_entry.content, update_entry.modifiedBy, entryId))
        conn.execute("INSERT INTO edits (entryId, modifiedBy, summary, content) VALUES (?, ?, ?, ?)", 
                     (entryId, update_entry.modifiedBy, update_entry.summary, update_entry.content))
    conn.close()
    return Entry(id=row[0], title=row[1], content=update_entry.content, lastModifiedBy=update_entry.modifiedBy, lastModifiedAt="2023-01-01T00:00:00")

@app.get("/entries/{entryId}/edits")
async def get_entry_edits(entryId: str = Path(..., min_length=1)):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM edits WHERE entryId=?", (entryId,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Entry not found")
    edits = [{"entryId": row[1], "modifiedBy": row[2], "summary": row[3], "content": row[4], "timestamp": row[5]} for row in rows]
    return edits

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)