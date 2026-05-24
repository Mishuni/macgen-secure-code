import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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

# API Handlers
async def get_entries(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    
    response_html = "<h1>Wiki Entries</h1><ul>"
    for entry in entries:
        response_html += f'<li><a href="/entries/{entry[0]}">{entry[1]}</a></li>'
    response_html += "</ul>"
    
    return web.Response(text=response_html, content_type='text/html')

async def create_entry(request):
    data = await request.json()
    if 'createdBy' not in data or 'title' not in data or 'content' not in data:
        return web.Response(text="Invalid input", status=400)

    entry_id = str(datetime.now().timestamp())
    created_by = data['createdBy']
    title = data['title']
    content = data['content']
    last_modified_at = datetime.now().isoformat()

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)',
                   (entry_id, title, content, created_by, last_modified_at))
    conn.commit()
    conn.close()

    return web.json_response({
        'id': entry_id,
        'title': title,
        'content': content,
        'lastModifiedBy': created_by,
        'lastModifiedAt': last_modified_at
    }, status=201)

async def get_entry(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()

    if entry is None:
        return web.Response(text="Entry not found", status=404)

    response_html = f"<h1>{entry[1]}</h1><p>{entry[2]}</p><p>Last modified by: {entry[3]} at {entry[4]}</p>"
    return web.Response(text=response_html, content_type='text/html')

async def update_entry(request):
    entry_id = request.match_info['entryId']
    data = await request.json()
    if 'modifiedBy' not in data or 'content' not in data or 'summary' not in data:
        return web.Response(text="Invalid input", status=400)

    modified_by = data['modifiedBy']
    content = data['content']
    summary = data['summary']
    modified_at = datetime.now().isoformat()

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()

    if entry is None:
        return web.Response(text="Entry not found", status=404)

    cursor.execute('UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?',
                   (content, modified_by, modified_at, entry_id))
    cursor.execute('INSERT INTO edits (entry_id, modified_by, summary, content, modified_at) VALUES (?, ?, ?, ?, ?)',
                   (entry_id, modified_by, summary, content, modified_at))
    conn.commit()
    conn.close()

    return web.json_response({
        'id': entry_id,
        'title': entry[1],
        'content': content,
        'lastModifiedBy': modified_by,
        'lastModifiedAt': modified_at
    })

async def get_edits(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entry_id = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()

    if not edits:
        return web.Response(text="Entry not found", status=404)

    response_html = f"<h1>Edit History for Entry {entry_id}</h1><ul>"
    for edit in edits:
        response_html += f'<li>{edit[2]} edited on {edit[5]}: {edit[3]}</li>'
    response_html += "</ul>"
    
    return web.Response(text=response_html, content_type='text/html')

# App setup
app = web.Application()
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_edits)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)