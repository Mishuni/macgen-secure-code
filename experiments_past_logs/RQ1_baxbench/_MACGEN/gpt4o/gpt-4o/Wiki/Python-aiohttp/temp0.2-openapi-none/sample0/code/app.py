import aiohttp
from aiohttp import web
import sqlite3
import json
from datetime import datetime

DATABASE = 'db.sqlite3'

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
            content TEXT NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT,
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

async def get_entries(request):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    entries_list = [{'id': entry['id'], 'title': entry['title']} for entry in entries]
    return web.json_response(entries_list)

async def create_entry(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')
    
    title = data.get('title')
    content = data.get('content')
    createdBy = data.get('createdBy')
    if not title or not content or not createdBy:
        return web.Response(status=400, text='Invalid input')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
        VALUES (?, ?, ?, ?)
    ''', (title, content, createdBy, datetime.now().isoformat()))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return web.json_response({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': createdBy, 'lastModifiedAt': datetime.now().isoformat()}, status=201)

async def get_entry(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id=?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    if entry:
        entry_data = {
            'id': entry['id'],
            'title': entry['title'],
            'content': entry['content'],
            'lastModifiedBy': entry['lastModifiedBy'],
            'lastModifiedAt': entry['lastModifiedAt']
        }
        return web.json_response(entry_data)
    else:
        return web.Response(status=404, text='Entry not found')

async def update_entry(request):
    entry_id = request.match_info['entryId']
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')
    
    content = data.get('content')
    modifiedBy = data.get('modifiedBy')
    summary = data.get('summary')
    if not content or not modifiedBy or not summary:
        return web.Response(status=400, text='Invalid input')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries WHERE id=?', (entry_id,))
    entry = cursor.fetchone()
    if not entry:
        conn.close()
        return web.Response(status=404, text='Entry not found')
    
    cursor.execute('''
        UPDATE entries
        SET content=?, lastModifiedBy=?, lastModifiedAt=?
        WHERE id=?
    ''', (content, modifiedBy, datetime.now().isoformat(), entry_id))
    cursor.execute('''
        INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt)
        VALUES (?, ?, ?, ?, ?)
    ''', (entry_id, content, modifiedBy, summary, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return web.json_response({'id': entry_id, 'title': entry[1], 'content': content, 'lastModifiedBy': modifiedBy, 'lastModifiedAt': datetime.now().isoformat()})

async def get_entry_edits(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entryId=?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()
    if edits:
        edits_list = [{'id': edit['id'], 'entryId': edit['entryId'], 'content': edit['content'], 'modifiedBy': edit['modifiedBy'], 'summary': edit['summary'], 'modifiedAt': edit['modifiedAt']} for edit in edits]
        return web.json_response(edits_list)
    else:
        return web.Response(status=404, text='Entry not found')

app = web.Application()
app.router.add_get('/entries', get_entries)
app.router.add_post('/entries', create_entry)
app.router.add_get('/entries/{entryId}', get_entry)
app.router.add_put('/entries/{entryId}', update_entry)
app.router.add_get('/entries/{entryId}/edits', get_entry_edits)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)