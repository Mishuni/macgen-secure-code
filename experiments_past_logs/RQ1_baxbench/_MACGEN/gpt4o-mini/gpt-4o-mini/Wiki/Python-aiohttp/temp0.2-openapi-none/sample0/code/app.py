import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
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
                modifiedBy TEXT,
                summary TEXT,
                content TEXT,
                modifiedAt TEXT,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            )
        ''')
        conn.commit()

# Validate input data
def validate_entry_data(data, is_update=False):
    if is_update:
        required_fields = ['content', 'modifiedBy', 'summary']
    else:
        required_fields = ['title', 'content', 'createdBy']
    
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or not data[field].strip():
            return False
    return True

# Get all entries
async def get_entries(request):
    async with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM entries')
        entries = cursor.fetchall()
    
    response_html = '<h1>Wiki Entries</h1><ul>'
    for entry in entries:
        response_html += f'<li><a href="/entries/{entry[0]}">{entry[1]}</a></li>'
    response_html += '</ul>'
    
    return web.Response(text=response_html, content_type='text/html')

# Create a new entry
async def create_entry(request):
    data = await request.json()
    if not validate_entry_data(data):
        return web.Response(text='Invalid input', status=400)

    title = data['title']
    content = data['content']
    created_by = data['createdBy']
    last_modified_at = datetime.now().isoformat()

    async with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)',
                       (title, content, created_by, last_modified_at))
        entry_id = cursor.lastrowid
        conn.commit()

    return web.json_response({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': created_by, 'lastModifiedAt': last_modified_at}, status=201)

# Get a specific entry
async def get_entry(request):
    entry_id = request.match_info['entryId']
    async with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()

    if entry is None:
        return web.Response(text='Entry not found', status=404)

    entry_html = f'<h1>{entry[1]}</h1><p>{entry[2]}</p><p>Last modified by: {entry[3]} at {entry[4]}</p>'
    return web.Response(text=entry_html, content_type='text/html')

# Update an existing entry
async def update_entry(request):
    entry_id = request.match_info['entryId']
    data = await request.json()
    if not validate_entry_data(data, is_update=True):
        return web.Response(text='Invalid input', status=400)

    content = data['content']
    modified_by = data['modifiedBy']
    summary = data['summary']
    modified_at = datetime.now().isoformat()

    async with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()

        if entry is None:
            return web.Response(text='Entry not found', status=404)

        cursor.execute('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
                       (content, modified_by, modified_at, entry_id))
        cursor.execute('INSERT INTO edits (entryId, modifiedBy, summary, content, modifiedAt) VALUES (?, ?, ?, ?, ?)',
                       (entry_id, modified_by, summary, content, modified_at))
        conn.commit()

    return web.json_response({'id': entry_id, 'title': entry[1], 'content': content, 'lastModifiedBy': modified_by, 'lastModifiedAt': modified_at})

# Get edit history for a specific entry
async def get_edits(request):
    entry_id = request.match_info['entryId']
    async with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM edits WHERE entryId = ?', (entry_id,))
        edits = cursor.fetchall()

    if not edits:
        return web.Response(text='Entry not found', status=404)

    edits_html = '<h1>Edit History</h1><ul>'
    for edit in edits:
        edits_html += f'<li>Modified by: {edit[2]} at {edit[5]} - Summary: {edit[3]}<br>Content: {edit[4]}</li>'
    edits_html += '</ul>'
    
    return web.Response(text=edits_html, content_type='text/html')

# Set up the web application
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