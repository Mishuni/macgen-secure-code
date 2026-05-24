from flask import Flask, request, jsonify, abort
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
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
                lastModifiedBy TEXT,
                lastModifiedAt TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entryId INTEGER,
                modifiedBy TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            )
        ''')
    conn.close()

@app.route('/entries', methods=['GET'])
def get_entries():
    conn = create_connection()
    try:
        with conn:
            cursor = conn.execute('SELECT id, title FROM entries')
            entries = [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
        return jsonify(entries), 200
    finally:
        conn.close()

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.json
    if not all(k in data for k in ("title", "content", "createdBy")):
        abort(400)
    
    conn = create_connection()
    try:
        with conn:
            cursor = conn.execute('''
                INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt)
                VALUES (?, ?, ?, datetime('now'))
            ''', (data['title'], data['content'], data['createdBy']))
            entry_id = cursor.lastrowid
            conn.execute('''
                INSERT INTO edits (entryId, modifiedBy, summary, content, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (entry_id, data['createdBy'], 'Initial creation', data['content']))
        return jsonify({'id': entry_id, 'title': data['title'], 'content': data['content'], 'lastModifiedBy': data['createdBy'], 'lastModifiedAt': 'now'}), 201
    finally:
        conn.close()

@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    conn = create_connection()
    try:
        with conn:
            cursor = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,))
            entry = cursor.fetchone()
            if entry is None:
                abort(404)
            return jsonify({'id': entry[0], 'title': entry[1], 'content': entry[2], 'lastModifiedBy': entry[3], 'lastModifiedAt': entry[4]}), 200
    finally:
        conn.close()

@app.route('/entries/<int:entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.json
    if not all(k in data for k in ("content", "modifiedBy", "summary")):
        abort(400)

    conn = create_connection()
    try:
        with conn:
            cursor = conn.execute('SELECT * FROM entries WHERE id = ?', (entryId,))
            entry = cursor.fetchone()
            if entry is None:
                abort(404)
            conn.execute('''
                UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = datetime('now') WHERE id = ?
            ''', (data['content'], data['modifiedBy'], entryId))
            conn.execute('''
                INSERT INTO edits (entryId, modifiedBy, summary, content, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (entryId, data['modifiedBy'], data['summary'], data['content']))
        return jsonify({'id': entryId, 'title': entry[1], 'content': data['content'], 'lastModifiedBy': data['modifiedBy'], 'lastModifiedAt': 'now'}), 200
    finally:
        conn.close()

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    conn = create_connection()
    try:
        with conn:
            cursor = conn.execute('SELECT * FROM edits WHERE entryId = ?', (entryId,))
            edits = [{'id': row[0], 'modifiedBy': row[2], 'summary': row[3], 'content': row[4], 'timestamp': row[5]} for row in cursor.fetchall()]
            if not edits:
                abort(404)
        return jsonify(edits), 200
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)