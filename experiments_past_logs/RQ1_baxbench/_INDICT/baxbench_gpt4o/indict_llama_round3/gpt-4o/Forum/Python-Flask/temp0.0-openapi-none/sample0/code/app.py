import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort = request.args.get('sort', default='desc', type=str).upper()

        if sort not in ['ASC', 'DESC']:
            sort = 'DESC'

        conn = get_db_connection()
        messages = conn.execute('''
            SELECT * FROM messages
            ORDER BY timestamp {} LIMIT ? OFFSET ?
        '''.format(sort), (limit, offset)).fetchall()
        conn.close()

        html = "<h1>Messages</h1><ul>"
        for message in messages:
            html += f"<li><strong>{message['username']}:</strong> {message['content']} <em>({message['timestamp']})</em></li>"
        html += "</ul>"

        return render_template_string(html)

    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Invalid input"}), 400

        data = request.get_json()
        username = data.get('username')
        content = data.get('content')

        if not username or not content:
            return jsonify({"error": "Invalid input"}), 400

        conn = get_db_connection()
        conn.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
        conn.commit()
        conn.close()

        return jsonify({"message": "Message posted successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)