from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_by TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                content TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                summary TEXT,
                created_at TEXT,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
        conn.commit()

@app.route('/entries', methods=['GET'])
def get_entries():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM entries')
        entries = cursor.fetchall()
        return jsonify([{'id': entry[0], 'title': entry[1]} for entry in entries])

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.json
    title = data['title']
    content = data['content']
    created_by = data['createdBy']
    
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO entries (title, content, created_by) VALUES (?, ?, ?)', (title, content, created_by))
        entry_id = cursor.lastrowid
        conn.commit()
        
    return jsonify({'id': entry_id, 'title': title, 'content': content, 'createdBy': created_by}), 201

@app.route('/entries/<int:entryId>', methods=['GET'])
def get_entry(entryId):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entryId,))
        entry = cursor.fetchone()
        if entry:
            return jsonify({
                'id': entry[0],
                'title': entry[1],
                'content': entry[2],
                'lastModifiedBy': entry[4],
                'lastModifiedAt': entry[5]
            })
        else:
            return 'Entry not found', 404

@app.route('/entries/<int:entryId>', methods=['PUT'])
def update_entry(entryId):
    data = request.json
    content = data['content']
    modified_by = data['modifiedBy']
    summary = data['summary']
    
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entryId,))
        entry = cursor.fetchone()
        if entry:
            cursor.execute('UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = datetime("now") WHERE id = ?', (content, modified_by, entryId))
            cursor.execute('INSERT INTO edits (entry_id, content, modified_by, summary, created_at) VALUES (?, ?, ?, ?, datetime("now"))', (entryId, content, modified_by, summary))
            conn.commit()
            return jsonify({'id': entryId, 'title': entry[1], 'content': content, 'lastModifiedBy': modified_by}), 200
        else:
            return 'Entry not found', 404

@app.route('/entries/<int:entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM edits WHERE entry_id = ?', (entryId,))
        edits = cursor.fetchall()
        if edits:
            return jsonify([{
                'content': edit[2],
                'modifiedBy': edit[3],
                'summary': edit[4],
                'createdAt': edit[5]
            } for edit in edits])
        else:
            return 'Entry not found', 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)