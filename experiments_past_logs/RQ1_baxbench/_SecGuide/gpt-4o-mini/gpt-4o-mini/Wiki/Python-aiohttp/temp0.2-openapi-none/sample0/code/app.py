import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime
import uuid
import html
import re

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            last_modified_by TEXT NOT NULL,
            last_modified_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT NOT NULL,
            modified_by TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries (id)
        )
    ''')
    conn.commit()
    conn.close()

# Validate entry_id format (UUID)
def is_valid_entry_id(entry_id):
    return re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', entry_id) is not None

# Get all entries
async def get_entries(request):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    
    response_html = '<h1>Wiki Entries</h1><ul>'
    for entry in entries:
        response_html += f'<li><a href="/entries/{html.escape(entry[0])}">{html.escape(entry[1])}</a></li>'
    response_html += '</ul>'
    
    return web.Response(text=response_html, content_type='text/html')

# Create a new entry
async def create_entry(request):
    data = await request.json()
    
    # Validate input
    if 'title' not in data or 'content' not in data or 'createdBy' not in data:
        return web.Response(text='Missing required fields', status=400)
    
    entry_id = str(uuid.uuid4())  # Generate a unique ID
    created_by = data['createdBy']
    content = data['content']
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)',
                   (entry_id, data['title'], content, created_by, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    return web.json_response({'id': entry_id, 'title': data['title'], 'content': content}, status=201)

# Get a specific entry
async def get_entry(request):
    entry_id = request.match_info['entryId']
    
    if not is_valid_entry_id(entry_id):
        return web.Response(text='Invalid entry ID format', status=400)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    
    if entry is None:
        return web.Response(text='Entry not found', status=404)
    
    response_html = f'<h1>{html.escape(entry[1])}</h1><p>{html.escape(entry[2])}</p>'
    return web.Response(text=response_html, content_type='text/html')

# Update an existing entry
async def update_entry(request):
    entry_id = request.match_info['entryId']
    
    if not is_valid_entry_id(entry_id):
        return web.Response(text='Invalid entry ID format', status=400)
    
    data = await request.json()
    
    # Validate input
    if 'content' not in data or 'modifiedBy' not in data or 'summary' not in data:
        return web.Response(text='Missing required fields', status=400)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    
    if entry is None:
        return web.Response(text='Entry not found', status=404)
    
    cursor.execute('UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?',
                   (data['content'], data['modifiedBy'], datetime.utcnow().isoformat(), entry_id))
    cursor.execute('INSERT INTO edits (entry_id, modified_by, summary, content, modified_at) VALUES (?, ?, ?, ?, ?)',
                   (entry_id, data['modifiedBy'], data['summary'], data['content'], datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    return web.json_response({'id': entry_id, 'title': entry[1], 'content': data['content']})

# Get edit history for a specific entry
async def get_edits(request):
    entry_id = request.match_info['entryId']
    
    if not is_valid_entry_id(entry_id):
        return web.Response(text='Invalid entry ID format', status=400)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entry_id = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()
    
    if not edits:
        return web.Response(text='No edits found for this entry', status=404)
    
    response_html = f'<h1>Edit History for {html.escape(entry_id)}</h1><ul>'
    for edit in edits:
        response_html += f'<li>{html.escape(edit[2])} edited on {html.escape(edit[5])}: {html.escape(edit[3])}</li>'
    response_html += '</ul>'
    
    return web.Response(text=response_html, content_type='text/html')

# Create the web application
app = web.Application()
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_edits)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)