import os
import sqlite3
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Configure SQLite database
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                lastModifiedBy TEXT NOT NULL,
                lastModifiedAt TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entryId TEXT NOT NULL,
                modifiedBy TEXT NOT NULL,
                summary TEXT NOT NULL,
                modifiedAt TEXT NOT NULL,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            )
        ''')
    print("Database initialized.")

@app.route('/entries', methods=['GET'])
def get_entries():
    with get_db() as conn:
        entries = conn.execute('SELECT * FROM entries').fetchall()
        return jsonify([dict(entry) for entry in entries])

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'createdBy' not in data:
        abort(400)
    
    entry_id = str(uuid.uuid4())
    last_modified_at = datetime.datetime.now().isoformat()
    
    with get_db() as conn:
        conn.execute('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)',
                     (entry_id, data['title'], data['content'], data['createdBy'], last_modified_at))
        conn.execute('INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?)',
                     (entry_id, data['createdBy'], 'Created entry', last_modified_at))
    
    return jsonify({'id': entry_id, 'title': data['title'], 'content': data['content'], 'lastModifiedBy': data['createdBy'], 'lastModifiedAt': last_modified_at}), 201

@app.route('/entries/<entryId>', methods=['GET'])
def get_entry(entryId):
    with get_db() as conn:
        entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
        if entry is None:
            abort(404)
        return jsonify(dict(entry))

@app.route('/entries/<entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.get_json()
    if not data or 'content' not in data or 'modifiedBy' not in data or 'summary' not in data:
        abort(400)

    last_modified_at = datetime.datetime.now().isoformat()
    
    with get_db() as conn:
        entry = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,)).fetchone()
        if entry is None:
            abort(404)
        
        conn.execute('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
                     (data['content'], data['modifiedBy'], last_modified_at, entryId))
        conn.execute('INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?)',
                     (entryId, data['modifiedBy'], data['summary'], last_modified_at))
    
    return jsonify({'id': entryId, 'content': data['content'], 'lastModifiedBy': data['modifiedBy'], 'lastModifiedAt': last_modified_at})

@app.route('/entries/<entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    with get_db() as conn:
        edits = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,)).fetchall()
        if edits is None:
            abort(404)
        return jsonify([dict(edit) for edit in edits])

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)