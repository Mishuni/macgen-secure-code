import aiohttp
from aiohttp import web
import sqlite3
import json
import html
from datetime import datetime

DATABASE = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            modified_by TEXT NOT NULL,
            summary TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries (id)
        )
    ''')
    conn.commit()
    conn.close()

# Get all entries
async def get_entries(request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    
    response_html = '<h1>Wiki Entries</h1><ul>'
    for entry in entries:
        entry_id, title = entry
        response_html += f'<li><a href="/entries/{entry_id}">{html.escape(title)}</a></li>'
    response_html += '</ul>'
    
    return web.Response(text=response_html, content_type='text/html')

# Create a new entry
async def create_entry(request):
    data = await request.json()
    title = data.get('title')
    content = data.get('content')
    created_by = data.get('createdBy')

    if not title or not content or not created_by:
        return web.Response(status=400, text='Missing required fields')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO entries (title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?)',
                   (title, content, created_by, datetime.now().isoformat()))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return web.json_response({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': created_by, 'lastModifiedAt': datetime.now().isoformat()}, status=201)

# Get a specific entry
async def get_entry(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()

    if entry is None:
        return web.Response(status=404, text='Entry not found')

    title, content, last_modified_by, last_modified_at = entry
    response_html = f'<h1>{html.escape(title)}</h1><p>{html.escape(content)}</p><p>Last modified by: {html.escape(last_modified_by)} at {last_modified_at}</p>'
    return web.Response(text=response_html, content_type='text/html')

# Update an existing entry
async def update_entry(request):
    entry_id = request.match_info['entryId']
    data = await request.json()
    content = data.get('content')
    modified_by = data.get('modifiedBy')
    summary = data.get('summary')

    if not content or not modified_by or not summary:
        return web.Response(status=400, text='Missing required fields')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?',
                   (content, modified_by, datetime.now().isoformat(), entry_id))
    if cursor.rowcount == 0:
        conn.close()
        return web.Response(status=404, text='Entry not found')

    cursor.execute('INSERT INTO edits (entry_id, modified_by, summary, modified_at) VALUES (?, ?, ?, ?)',
                   (entry_id, modified_by, summary, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return web.json_response({'id': entry_id, 'content': content, 'lastModifiedBy': modified_by, 'lastModifiedAt': datetime.now().isoformat()}, status=200)

# Get edit history for a specific entry
async def get_edit_history(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT modified_by, summary, modified_at FROM edits WHERE entry_id = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()

    if not edits:
        return web.Response(status=404, text='Entry not found')

    response_html = f'<h1>Edit History for Entry {entry_id}</h1><ul>'
    for edit in edits:
        modified_by, summary, modified_at = edit
        response_html += f'<li>{html.escape(summary)} by {html.escape(modified_by)} at {modified_at}</li>'
    response_html += '</ul>'
    
    return web.Response(text=response_html, content_type='text/html')

# Set up the application and routes
app = web.Application()
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_edit_history)

# Initialize the database and run the app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)