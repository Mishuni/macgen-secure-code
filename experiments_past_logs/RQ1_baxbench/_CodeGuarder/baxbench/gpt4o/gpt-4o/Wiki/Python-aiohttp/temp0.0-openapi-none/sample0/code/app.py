import os
import sqlite3
from aiohttp import web
import json
from datetime import datetime

DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId TEXT,
            modifiedBy TEXT,
            summary TEXT,
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

# Validate environment variable
def validate_env_var(var_name, expected_prefix):
    value = os.getenv(var_name)
    if not value or not value.startswith(expected_prefix):
        raise ValueError(f"Invalid or missing environment variable: {var_name}")
    return value

# Define data models
def get_entry_by_id(entry_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    return entry

def get_edits_by_entry_id(entry_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entryId = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()
    return edits

# Create the Aiohttp Web Application
app = web.Application()

# Implement API Endpoints
async def get_entries(request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    return web.json_response([{'id': entry[0], 'title': entry[1]} for entry in entries])

async def create_entry(request):
    try:
        data = await request.json()
        entry_id = str(uuid.uuid4())
        title = data['title']
        content = data['content']
        created_by = data['createdBy']
        last_modified_at = datetime.utcnow().isoformat()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, title, content, created_by, last_modified_at))
        conn.commit()
        conn.close()

        return web.json_response({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': created_by, 'lastModifiedAt': last_modified_at}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

async def get_entry(request):
    entry_id = request.match_info['entryId']
    entry = get_entry_by_id(entry_id)
    if entry:
        return web.json_response({'id': entry[0], 'title': entry[1], 'content': entry[2], 'lastModifiedBy': entry[3], 'lastModifiedAt': entry[4]})
    else:
        return web.json_response({'error': 'Entry not found'}, status=404)

async def update_entry(request):
    entry_id = request.match_info['entryId']
    entry = get_entry_by_id(entry_id)
    if not entry:
        return web.json_response({'error': 'Entry not found'}, status=404)

    try:
        data = await request.json()
        content = data['content']
        modified_by = data['modifiedBy']
        summary = data['summary']
        last_modified_at = datetime.utcnow().isoformat()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE entries
            SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
            WHERE id = ?
        ''', (content, modified_by, last_modified_at, entry_id))
        cursor.execute('''
            INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, modified_by, summary, last_modified_at))
        conn.commit()
        conn.close()

        return web.json_response({'id': entry_id, 'title': entry[1], 'content': content, 'lastModifiedBy': modified_by, 'lastModifiedAt': last_modified_at})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

async def get_entry_edits(request):
    entry_id = request.match_info['entryId']
    entry = get_entry_by_id(entry_id)
    if not entry:
        return web.json_response({'error': 'Entry not found'}, status=404)

    edits = get_edits_by_entry_id(entry_id)
    return web.json_response([{'id': edit[0], 'entryId': edit[1], 'modifiedBy': edit[2], 'summary': edit[3], 'modifiedAt': edit[4]} for edit in edits])

# Setup routes
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_entry_edits)

# Initialize the database
init_db()

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)