from flask import Flask, request, jsonify, render_template, abort, redirect, url_for
import sqlite3
from datetime import datetime
import os
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Secret key for CSRF protection
csrf = CSRFProtect(app)

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
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
            modifiedAt TEXT,
            summary TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/entries', methods=['GET'])
def get_entries():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, title FROM entries')
    entries = c.fetchall()
    conn.close()
    return render_template('entries.html', entries=entries)

@app.route('/entries', methods=['POST'])
@csrf.exempt  # CSRF protection for API endpoints
def create_entry():
    data = request.json
    if not data or 'title' not in data or 'content' not in data or 'createdBy' not in data:
        abort(400, 'Invalid request payload')
    
    title = data['title'].strip()
    content = data['content'].strip()
    createdBy = data['createdBy'].strip()

    if not title or not content or not createdBy:
        abort(400, 'Title, content, and createdBy cannot be empty')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)', 
              (title, content, createdBy, datetime.now().isoformat()))
    entry_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': entry_id, 'title': title, 'content': content}), 201

@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?', (entryId,))
    entry = c.fetchone()
    conn.close()
    if entry:
        return render_template('entry.html', entry=entry)
    else:
        abort(404, 'Entry not found')

@app.route('/entries/<int:entryId>', methods=['PUT'])
@csrf.exempt  # CSRF protection for API endpoints
def update_entry(entryId):
    data = request.json
    if not data or 'content' not in data or 'modifiedBy' not in data or 'summary' not in data:
        abort(400, 'Invalid request payload')
    
    content = data['content'].strip()
    modifiedBy = data['modifiedBy'].strip()
    summary = data['summary'].strip()

    if not content or not modifiedBy or not summary:
        abort(400, 'Content, modifiedBy, and summary cannot be empty')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM entries WHERE id = ?', (entryId,))
    if not c.fetchone():
        conn.close()
        abort(404, 'Entry not found')
    
    c.execute('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
              (content, modifiedBy, datetime.now().isoformat(), entryId))
    c.execute('INSERT INTO edits (entryId, content, modifiedBy, modifiedAt, summary) VALUES (?, ?, ?, ?, ?)', 
              (entryId, content, modifiedBy, datetime.now().isoformat(), summary))
    conn.commit()
    conn.close()
    return jsonify({'id': entryId, 'content': content}), 200

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM entries WHERE id = ?', (entryId,))
    if not c.fetchone():
        conn.close()
        abort(404, 'Entry not found')
    
    c.execute('SELECT content, modifiedBy, modifiedAt, summary FROM edits WHERE entryId = ?', (entryId,))
    edits = c.fetchall()
    conn.close()
    return render_template('edits.html', edits=edits)

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }).data
    response.content_type = "application/json"
    return response

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')  # Use HTTPS in development