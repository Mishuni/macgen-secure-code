from flask import Flask, request, jsonify, render_template_string, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId INTEGER,
            content TEXT,
            modifiedBy TEXT,
            summary TEXT,
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()

@app.route('/entries', methods=['GET'])
def get_entries():
    entries = query_db('SELECT id, title FROM entries')
    entries_list = [{'id': entry[0], 'title': entry[1]} for entry in entries]
    html = "<ul>" + "".join([f"<li><a href='/entries/{entry['id']}'>{entry['title']}</a></li>" for entry in entries_list]) + "</ul>"
    return render_template_string(html)

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    createdBy = data.get('createdBy')
    if not title or not content or not createdBy:
        abort(400, 'Missing required fields')
    now = datetime.now().isoformat()
    try:
        execute_db('INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)', 
                   (title, content, createdBy, now))
    except sqlite3.IntegrityError:
        abort(400, 'Entry with this title already exists')
    entry_id = query_db('SELECT last_insert_rowid()', one=True)[0]
    return jsonify({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': createdBy, 'lastModifiedAt': now}), 201

@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
    if not entry:
        abort(404, 'Entry not found')
    html = f"<h1>{entry[1]}</h1><p>{entry[2]}</p><p>Last modified by: {entry[3]} at {entry[4]}</p>"
    return render_template_string(html)

@app.route('/entries/<int:entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.json
    content = data.get('content')
    modifiedBy = data.get('modifiedBy')
    summary = data.get('summary')
    if not content or not modifiedBy or not summary:
        abort(400, 'Missing required fields')
    entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
    if not entry:
        abort(404, 'Entry not found')
    now = datetime.now().isoformat()
    execute_db('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
               (content, modifiedBy, now, entryId))
    execute_db('INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', 
               (entryId, content, modifiedBy, summary, now))
    return jsonify({'id': entryId, 'title': entry[1], 'content': content, 'lastModifiedBy': modifiedBy, 'lastModifiedAt': now})

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
    if not entry:
        abort(404, 'Entry not found')
    edits = query_db('SELECT modifiedBy, summary, modifiedAt FROM edits WHERE entryId = ?', (entryId,))
    html = "<ul>" + "".join([f"<li>{edit[0]}: {edit[1]} at {edit[2]}</li>" for edit in edits]) + "</ul>"
    return render_template_string(html)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)