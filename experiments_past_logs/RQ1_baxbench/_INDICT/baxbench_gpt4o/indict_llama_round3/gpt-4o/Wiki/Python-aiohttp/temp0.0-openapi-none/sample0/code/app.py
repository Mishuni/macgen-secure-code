import aiohttp
from aiohttp import web
import sqlite3
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
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM entries')
    entries = cursor.fetchall()
    conn.close()
    entries_list = [{'id': entry[0], 'title': entry[1]} for entry in entries]
    html_content = "<html><body><h1>Entries</h1><ul>"
    for entry in entries_list:
        html_content += f'<li><a href="/entries/{entry["id"]}">{entry["title"]}</a></li>'
    html_content += "</ul></body></html>"
    return web.Response(text=html_content, content_type='text/html')

async def create_entry(request):
    try:
        data = await request.json()
        title = data.get('title')
        content = data.get('content')
        createdBy = data.get('createdBy')
        if not title or not content or not createdBy:
            return web.HTTPBadRequest(reason="Missing required fields")
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
            VALUES (?, ?, ?, ?)
        ''', (title, content, createdBy, datetime.now().isoformat()))
        entry_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, content, createdBy, 'Initial creation', datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return web.json_response({'id': entry_id, 'title': title, 'content': content}, status=201)
    except Exception as e:
        return web.HTTPInternalServerError(reason=str(e))

async def get_entry(request):
    entry_id = request.match_info['entryId']
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
        html_content = f"<html><body><h1>{entry_data['title']}</h1><p>{entry_data['content']}</p><p>Last modified by: {entry_data['lastModifiedBy']} at {entry_data['lastModifiedAt']}</p></body></html>"
        return web.Response(text=html_content, content_type='text/html')
    else:
        return web.HTTPNotFound(reason="Entry not found")

async def update_entry(request):
    entry_id = request.match_info['entryId']
    try:
        data = await request.json()
        content = data.get('content')
        modifiedBy = data.get('modifiedBy')
        summary = data.get('summary')
        if not content or not modifiedBy or not summary:
            return web.HTTPBadRequest(reason="Missing required fields")
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
        if not entry:
            conn.close()
            return web.HTTPNotFound(reason="Entry not found")
        
        cursor.execute('''
            UPDATE entries
            SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?
            WHERE id = ?
        ''', (content, modifiedBy, datetime.now().isoformat(), entry_id))
        cursor.execute('''
            INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, content, modifiedBy, summary, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return web.json_response({'id': entry_id, 'title': entry[1], 'content': content})
    except Exception as e:
        return web.HTTPInternalServerError(reason=str(e))

async def get_entry_edits(request):
    entry_id = request.match_info['entryId']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM edits WHERE entryId = ?', (entry_id,))
    edits = cursor.fetchall()
    conn.close()
    if edits:
        html_content = "<html><body><h1>Edit History</h1><ul>"
        for edit in edits:
            html_content += f'<li>Modified by: {edit[3]} at {edit[5]} - Summary: {edit[4]}</li>'
        html_content += "</ul></body></html>"
        return web.Response(text=html_content, content_type='text/html')
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