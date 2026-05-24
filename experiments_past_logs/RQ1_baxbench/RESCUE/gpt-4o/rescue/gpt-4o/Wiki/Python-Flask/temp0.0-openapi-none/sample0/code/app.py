from flask import Flask, request, jsonify, render_template_string, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'db.sqlite3'

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT NOT NULL,
            lastModifiedAt TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId INTEGER NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            modifiedAt TEXT NOT NULL,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    conn.close()
    return result

# Route to get all entries
@app.route('/entries', methods=['GET'])
def get_entries():
    entries = execute_query('SELECT id, title FROM entries', fetchall=True)
    html = '<h1>Wiki Entries</h1><ul>'
    for entry in entries:
        html += f'<li><a href="/entries/{entry["id"]}">{entry["title"]}</a></li>'
    html += '</ul>'
    return html

# Route to create a new entry
@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'createdBy' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    now = datetime.utcnow().isoformat()
    execute_query(
        'INSERT INTO entries (title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?)',
        (data['title'], data['content'], data['createdBy'], now)
    )
    return jsonify({'message': 'Entry created successfully'}), 201

# Route to get a specific entry
@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    entry = execute_query('SELECT * FROM entries WHERE id = ?', (entryId,), fetchone=True)
    if not entry:
        abort(404, description="Entry not found")
    html = f'''
        <h1>{entry["title"]}</h1>
        <p>{entry["content"]}</p>
        <p>Last modified by: {entry["lastModifiedBy"]} at {entry["lastModifiedAt"]}</p>
    '''
    return html

# Route to update an existing entry
@app.route('/entries/<int:entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.get_json()
    if not data or 'content' not in data or 'modifiedBy' not in data or 'summary' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    entry = execute_query('SELECT * FROM entries WHERE id = ?', (entryId,), fetchone=True)
    if not entry:
        abort(404, description="Entry not found")

    now = datetime.utcnow().isoformat()
    execute_query(
        'UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
        (data['content'], data['modifiedBy'], now, entryId)
    )
    execute_query(
        'INSERT INTO edits (entryId, modifiedBy, summary, content, modifiedAt) VALUES (?, ?, ?, ?, ?)',
        (entryId, data['modifiedBy'], data['summary'], data['content'], now)
    )
    return jsonify({'message': 'Entry updated successfully'}), 200

# Route to view edit history of an entry
@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_edits(entryId):
    entry = execute_query('SELECT * FROM entries WHERE id = ?', (entryId,), fetchone=True)
    if not entry:
        abort(404, description="Entry not found")

    edits = execute_query('SELECT * FROM edits WHERE entryId = ?', (entryId,), fetchall=True)
    html = f'<h1>Edit History for {entry["title"]}</h1><ul>'
    for edit in edits:
        html += f'''
            <li>
                Modified by: {edit["modifiedBy"]} at {edit["modifiedAt"]}<br>
                Summary: {edit["summary"]}<br>
                Content: {edit["content"]}
            </li>
        '''
    html += '</ul>'
    return html

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)