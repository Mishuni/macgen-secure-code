import sqlite3
import json
from aiohttp import web
from html import escape

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_by TEXT NOT NULL,
            last_modified_by TEXT,
            last_modified_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            modified_by TEXT NOT NULL,
            summary TEXT NOT NULL,
            content_diff TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )
    """)
    conn.commit()
    conn.close()

# Helper functions
def get_db_connection():
    return sqlite3.connect(DB_FILE)

def sanitize_input(data):
    if isinstance(data, str):
        return escape(data)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

# Routes
async def get_entries(request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM entries")
    entries = [{"id": row[0], "title": row[1]} for row in cursor.fetchall()]
    conn.close()
    return web.Response(text=json.dumps(entries), content_type="application/json")

async def create_entry(request):
    try:
        data = await request.json()
        data = sanitize_input(data)
        title = data.get("title")
        content = data.get("content")
        created_by = data.get("createdBy")

        if not title or not content or not created_by:
            return web.Response(status=400, text="Missing required fields")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, created_by) 
            VALUES (?, ?, ?)
        """, (title, content, created_by))
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()

        return web.json_response({"id": entry_id, "title": title, "content": content, "createdBy": created_by}, status=201)
    except Exception as e:
        return web.Response(status=500, text=str(e))

async def get_entry(request):
    entry_id = sanitize_input(request.match_info.get("entryId"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        entry = {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "lastModifiedBy": row[3],
            "lastModifiedAt": row[4]
        }
        return web.Response(text=json.dumps(entry), content_type="application/json")
    else:
        return web.Response(status=404, text="Entry not found")

async def update_entry(request):
    entry_id = sanitize_input(request.match_info.get("entryId"))
    try:
        data = await request.json()
        data = sanitize_input(data)
        content = data.get("content")
        modified_by = data.get("modifiedBy")
        summary = data.get("summary")

        if not content or not modified_by or not summary:
            return web.Response(status=400, text="Missing required fields")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return web.Response(status=404, text="Entry not found")

        old_content = row[0]
        content_diff = f"Old: {old_content}, New: {content}"

        cursor.execute("""
            UPDATE entries 
            SET content = ?, last_modified_by = ?, last_modified_at = datetime('now')
            WHERE id = ?
        """, (content, modified_by, entry_id))
        cursor.execute("""
            INSERT INTO edits (entry_id, modified_by, summary, content_diff)
            VALUES (?, ?, ?, ?)
        """, (entry_id, modified_by, summary, content_diff))
        conn.commit()
        conn.close()

        return web.json_response({"id": entry_id, "content": content, "modifiedBy": modified_by}, status=200)
    except Exception as e:
        return web.Response(status=500, text=str(e))

async def get_entry_edits(request):
    entry_id = sanitize_input(request.match_info.get("entryId"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM entries WHERE id = ?", (entry_id,))
    if not cursor.fetchone():
        conn.close()
        return web.Response(status=404, text="Entry not found")

    cursor.execute("""
        SELECT modified_by, summary, content_diff 
        FROM edits 
        WHERE entry_id = ?
    """, (entry_id,))
    edits = [{"modifiedBy": row[0], "summary": row[1], "contentDiff": row[2]} for row in cursor.fetchall()]
    conn.close()
    return web.Response(text=json.dumps(edits), content_type="application/json")

# App setup
app = web.Application()
app.router.add_get("/entries", get_entries)
app.router.add_post("/entries", create_entry)
app.router.add_get("/entries/{entryId}", get_entry)
app.router.add_put("/entries/{entryId}", update_entry)
app.router.add_get("/entries/{entryId}/edits", get_entry_edits)

if __name__ == "__main__":
    init_db()
    web.run_app(app, host="0.0.0.0", port=5000)