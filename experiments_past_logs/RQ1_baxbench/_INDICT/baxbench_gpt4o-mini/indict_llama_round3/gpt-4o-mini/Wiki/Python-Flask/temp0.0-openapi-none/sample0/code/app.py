from flask import Flask, request, jsonify, render_template_string
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

def init_db():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_at TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                modified_by TEXT,
                summary TEXT,
                content TEXT,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
    conn.close()

@app.route('/entries', methods=['GET'])
def get_entries():
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT id, title FROM entries')
        entries = cursor.fetchall()
    return render_template_string('<ul>{% for entry in entries %}<li><a href="/entries/{{ entry[0] }}">{{ entry[1] }}</a></li>{% endfor %}</ul>', entries=entries)

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.json
    title = data['title']
    content = data['content']
    created_by = data['createdBy']
    
    conn = create_connection()
    with conn:
        cursor = conn.execute('INSERT INTO entries (title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?)', (title, content, created_by, datetime.now().isoformat()))
        entry_id = cursor.lastrowid
    return jsonify({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': created_by, 'lastModifiedAt': datetime.now().isoformat()}), 201

@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,))
        entry = cursor.fetchone()
    if entry:
        return render_template_string('<h1>{{ entry[1] }}</h1><p>{{ entry[2] }}</p>', entry=entry)
    return 'Entry not found', 404

@app.route('/entries/<int:entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.json
    content = data['content']
    modified_by = data['modifiedBy']
    summary = data['summary']
    
    conn = create_connection()
    with conn:
        cursor = conn.execute('UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?', (content, modified_by, datetime.now().isoformat(), entryId))
        if cursor.rowcount == 0:
            return 'Entry not found', 404
        conn.execute('INSERT INTO edits (entry_id, modified_by, summary, content) VALUES (?, ?, ?, ?)', (entryId, modified_by, summary, content))
    return jsonify({'id': entryId, 'content': content, 'lastModifiedBy': modified_by, 'lastModifiedAt': datetime.now().isoformat()}), 200

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM edits WHERE entry_id = ?', (entryId,))
        edits = cursor.fetchall()
    if edits:
        return render_template_string('<ul>{% for edit in edits %}<li>{{ edit[2] }}: {{ edit[3] }} - {{ edit[4] }}</li>{% endfor %}</ul>', edits=edits)
    return 'No edits found for this entry', 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)