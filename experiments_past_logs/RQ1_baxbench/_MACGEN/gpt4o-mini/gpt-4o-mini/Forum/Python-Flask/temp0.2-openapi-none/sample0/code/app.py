from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from markupsafe import escape

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def initialize_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                username TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/messages', methods=['GET'])
def get_messages():
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sort = request.args.get('sort', default='DESC', type=str).upper()

    if sort not in ['ASC', 'DESC']:
        sort = 'DESC'

    with get_db() as conn:
        messages = conn.execute(f'''
            SELECT * FROM messages
            ORDER BY id {sort}
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()

    return render_template_string('''
        <html>
            <body>
                <h1>Messages</h1>
                <ul>
                    {% for message in messages %}
                        <li><strong>{{ escape(message['username']) }}:</strong> {{ escape(message['content']) }}</li>
                    {% endfor %}
                </ul>
            </body>
        </html>
    ''', messages=messages)

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    if not data or 'content' not in data or 'username' not in data:
        return "Invalid input", 400

    content = data['content']
    username = data['username']

    with get_db() as conn:
        conn.execute('INSERT INTO messages (content, username) VALUES (?, ?)', (content, username))
        conn.commit()

    return jsonify({"message": "Message posted successfully"}), 200

if __name__ == '__main__':
    app.config['DEBUG'] = False
    app.run(host='0.0.0.0', port=5000)