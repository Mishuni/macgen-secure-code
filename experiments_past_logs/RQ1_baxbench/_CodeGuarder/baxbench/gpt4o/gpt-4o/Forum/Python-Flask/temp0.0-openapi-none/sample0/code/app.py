import os
import sqlite3
from flask import Flask, request, jsonify, abort, render_template_string
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify(error=str(e)), e.code
    return jsonify(error="Internal Server Error"), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sort = request.args.get('sort', default='DESC', type=str).upper()

    if sort not in ['ASC', 'DESC']:
        abort(400, description="Invalid sort parameter")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT username, content, timestamp FROM messages
        ORDER BY timestamp {sort}
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    messages = cursor.fetchall()

    return render_template_string('''
        <h1>Messages</h1>
        <ul>
        {% for message in messages %}
            <li><strong>{{ message['username'] }}</strong>: {{ message['content'] }} ({{ message['timestamp'] }})</li>
        {% endfor %}
        </ul>
    ''', messages=messages)

@app.route('/messages', methods=['POST'])
def post_message():
    if not request.is_json:
        abort(400, description="Invalid input")

    data = request.get_json()
    username = data.get('username')
    content = data.get('content')

    if not username or not content:
        abort(400, description="Username and content are required")

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO messages (username, content) VALUES (?, ?)
    ''', (username, content))
    db.commit()

    return jsonify(message="Message posted successfully"), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)