from flask import Flask, request, jsonify, render_template, abort
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = 'db.sqlite3'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        app.logger.error(f"Database connection error: {e}")
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

def validate_entry_data(data):
    if not data.get('title') or not data.get('content') or not data.get('createdBy'):
        return False
    if len(data['title']) > 100 or len(data['content']) > 1000:
        return False
    return True

@app.route('/entries', methods=['GET'])
def get_entries():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM entries")
        entries = cursor.fetchall()
        return render_template('entries_list.html', entries=entries)

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not validate_entry_data(data):
        return jsonify({'error': 'Invalid input data'}), 400

    title = data.get('title')
    content = data.get('content')
    created_by = data.get('createdBy')

    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (title, content, last_modified_by) VALUES (?, ?, ?)", (title, content, created_by))
        entry_id = cursor.lastrowid
        return jsonify({'id': entry_id, 'title': title, 'content': content, 'lastModifiedBy': created_by}), 201

@app.route('/entries/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
        entry = cursor.fetchone()
        if entry:
            return render_template('entry_detail.html', entry=entry)
        else:
            abort(404)

@app.route('/entries/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = request.get_json()
    content = data.get('content')
    modified_by = data.get('modifiedBy')
    summary = data.get('summary')

    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE entries SET content=?, last_modified_by=? WHERE id=?", (content, modified_by, entry_id))
        if cursor.rowcount == 0:
            abort(404)
        cursor.execute("INSERT INTO edits (entry_id, modified_by, summary, content) VALUES (?, ?, ?, ?)", (entry_id, modified_by, summary, content))
        return jsonify({'id': entry_id, 'content': content, 'lastModifiedBy': modified_by}), 200

@app.route('/entries/<int:entry_id>/edits', methods=['GET'])
def get_entry_edits(entry_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM edits WHERE entry_id=?", (entry_id,))
        edits = cursor.fetchall()
        if edits:
            return render_template('edits_list.html', edits=edits)
        else:
            abort(404)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)