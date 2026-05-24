import aiohttp
from aiohttp import web
import sqlite3
import json

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_by TEXT NOT NULL,
            last_modified_by TEXT,
            last_modified_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER,
            modified_by TEXT NOT NULL,
            summary TEXT,
            content TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries (id)
        )
    ''')
    conn.commit()
    conn.close()

# Create a new entry
async def create_entry(request):
    data = await request.json()
    title = data['title']
    content = data['content']
    created_by = data['createdBy']

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO entries (title, content, created_by) VALUES (?, ?, ?)", (title, content, created_by))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return web.json_response({'id': entry_id, 'title': title, 'content': content, 'createdBy': created_by}, status=201)

# Get all entries
async def get_entries(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM entries")
    entries = cursor.fetchall()
    conn.close()

    return web.Response(text=json.dumps(entries), content_type='text/html')

# Get a specific entry
async def get_entry(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    conn.close()

    if entry is None:
        return web.Response(status=404)

    return web.Response(text=json.dumps(entry), content_type='text/html')

# Update an existing entry
async def update_entry(request):
    entry_id = request.match_info['entryId']
    data = await request.json()
    content = data['content']
    modified_by = data['modifiedBy']
    summary = data['summary']

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("UPDATE entries SET content = ?, last_modified_by = ? WHERE id = ?", (content, modified_by, entry_id))
    if cursor.rowcount == 0:
        conn.close()
        return web.Response(status=404)

    cursor.execute("INSERT INTO edits (entry_id, modified_by, summary, content) VALUES (?, ?, ?, ?)", (entry_id, modified_by, summary, content))
    conn.commit()
    conn.close()

    return web.Response(text=json.dumps({'id': entry_id, 'content': content}), content_type='application/json')

# Get edit history for a specific entry
async def get_edit_history(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM edits WHERE entry_id = ?", (entry_id,))
    edits = cursor.fetchall()
    conn.close()

    if edits is None:
        return web.Response(status=404)

    return web.Response(text=json.dumps(edits), content_type='text/html')

# Set up the web application
app = web.Application()
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries', get_entries)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_edit_history)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)