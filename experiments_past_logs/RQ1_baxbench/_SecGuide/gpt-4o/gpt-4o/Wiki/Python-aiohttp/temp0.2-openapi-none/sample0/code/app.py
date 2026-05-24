import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime
import os

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
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
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

def validate_input(data, required_fields):
    if not isinstance(data, dict):
        return False
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or not data[field].strip():
            return False
        if len(data[field]) > 255:  # Limit input size to 255 characters
            return False
    return True

async def get_entries(request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    entries_list = [{'id': entry[0], 'title': entry[1]} for entry in entries]
    return web.json_response(entries_list)

async def create_entry(request):
    try:
        data = await request.json()
        if not validate_input(data, ['title', 'content', 'createdBy']):
            raise ValueError("Invalid input")
        title = data['title'].strip()
        content = data['content'].strip()
        createdBy = data['createdBy'].strip()
    except (json.JSONDecodeError, KeyError, ValueError):
        return web.HTTPBadRequest(reason="Invalid input")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
        VALUES (?, ?, ?, ?)
    ''', (title, content, createdBy, datetime.now().isoformat()))
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()

    return web.json_response({'id': entry_id, 'title': title, 'content': content}, status=201)

async def get_entry(request):
    entry_id = request.match_info.get('entryId')
    if not entry_id.isdigit():
        return web.HTTPBadRequest(reason="Invalid entry ID")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()

    if entry:
        entry_data = {
            'id': entry[0],
            'title': entry[1],
            'content': entry[2],
            'lastModifiedBy': entry[3],
            'lastModifiedAt': entry[4]
        }
        return web.json_response(entry_data)
    else:
        return web.HTTPNotFound(reason="Entry not found")

async def update_entry(request):
    entry_id = request.match_info.get('entryId')
    if not entry_id.isdigit():
        return web.HTTPBadRequest(reason="Invalid entry ID")
    
    try:
        data = await request.json()
        if not validate_input(data, ['content', 'modifiedBy', 'summary']):
            raise ValueError("Invalid input")
        content = data['content'].strip()
        modifiedBy = data['modifiedBy'].strip()
        summary = data['summary'].strip()
    except (json.JSONDecodeError, KeyError, ValueError):
        return web.HTTPBadRequest(reason="Invalid input")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()

    if entry:
        cursor.execute('''
            UPDATE entries
            SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
            WHERE id = ?
        ''', (content, modifiedBy, datetime.now().isoformat(), entry_id))
        cursor.execute('''
            INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, modifiedBy, summary, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return web.json_response({'id': entry_id, 'title': entry[1], 'content': content})
    else:
        conn.close()
        return web.HTTPNotFound(reason="Entry not found")

async def get_entry_edits(request):
    entry_id = request.match_info.get('entryId')
    if not entry_id.isdigit():
        return web.HTTPBadRequest(reason="Invalid entry ID")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entryId = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()

    if edits:
        edits_list = [{'id': edit[0], 'entryId': edit[1], 'modifiedBy': edit[2], 'summary': edit[3], 'modifiedAt': edit[4]} for edit in edits]
        return web.json_response(edits_list)
    else:
        return web.HTTPNotFound(reason="Entry not found")

app = web.Application()
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_entry_edits)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)