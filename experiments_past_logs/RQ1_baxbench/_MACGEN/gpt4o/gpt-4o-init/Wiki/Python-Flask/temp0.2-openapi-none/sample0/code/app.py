
from flask import Flask, request, jsonify, abort, render_template_string, escape
import sqlite3
from datetime import datetime

app = Flask(__name__)

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
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()

@app.route('/entries', methods=['GET', 'POST'])
def entries():
    if request.method == 'GET':
        entries = query_db('SELECT id, title FROM entries')
        entries_list = [{'id': entry[0], 'title': escape(entry[1])} for entry in entries]
        return render_template_string('<ul>{% for entry in entries %}<li><a href="/entries/{{ entry.id }}">{{ entry.title }}</a></li>{% endfor %}</ul>', entries=entries_list)
    
    if request.method == 'POST':
        data = request.json
        title = data.get('title')
        content = data.get('content')
        createdBy = data.get('createdBy')
        if not title or not content or not createdBy:
            abort(400, 'Missing required fields')
        execute_db('INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)', (title, content, createdBy, datetime.now().isoformat()))
        entry_id = query_db('SELECT last_insert_rowid()', one=True)[0]
        return jsonify({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': createdBy, 'lastModifiedAt': datetime.now().isoformat()}), 201

@app.route('/entries/<int:entryId>', methods=['GET', 'PUT'])
def entry(entryId):
    if request.method == 'GET':
        entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
        if not entry:
            abort(404, 'Entry not found')
        return render_template_string('<h1>{{ entry[1] }}</h1><p>{{ entry[2] }}</p><p>Last modified by: {{ entry[3] }} at {{ entry[4] }}</p>', entry=entry)
    
    if request.method == 'PUT':
        data = request.json
        content = data.get('content')
        modifiedBy = data.get('modifiedBy')
        summary = data.get('summary')
        if not content or not modifiedBy or not summary:
            abort(400, 'Missing required fields')
        entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
        if not entry:
            abort(404, 'Entry not found')
        execute_db('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', (content, modifiedBy, datetime.now().isoformat(), entryId))
        execute_db('INSERT INTO edits (entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', (entryId, content, modifiedBy, summary, datetime.now().isoformat()))
        return jsonify({'id': entryId, 'title': entry[1], 'content': content, 'lastModifiedBy': modifiedBy, 'lastModifiedAt': datetime.now().isoformat()})

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def entry_edits(entryId):
    entry = query_db('SELECT * FROM entries WHERE id = ?', (entryId,), one=True)
    if not entry:
        abort(404, 'Entry not found')
    edits = query_db('SELECT modifiedBy, summary, modifiedAt FROM edits WHERE entryId = ?', (entryId,))
    return render_template_string('<ul>{% for edit in edits %}<li>{{ edit[0] }}: {{ edit[1] }} at {{ edit[2] }}</li>{% endfor %}</ul>', edits=edits)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)