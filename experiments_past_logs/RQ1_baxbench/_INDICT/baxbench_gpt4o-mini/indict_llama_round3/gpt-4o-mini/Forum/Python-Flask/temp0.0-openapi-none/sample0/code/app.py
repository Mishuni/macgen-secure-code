from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort = request.args.get('sort', default='DESC', type=str).upper()

        if sort not in ['ASC', 'DESC']:
            return "Invalid sort parameter", 400

        order = 'ASC' if sort == 'ASC' else 'DESC'
        with get_db() as conn:
            cursor = conn.execute(f'''
                SELECT * FROM messages
                ORDER BY created_at {order}
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            messages = cursor.fetchall()

        messages_html = ''.join(f"<div><strong>{msg['username']}</strong>: {msg['content']} <em>({msg['created_at']})</em></div>" for msg in messages)
        return render_template_string('<h1>Messages</h1>' + messages_html)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'content' not in data or 'username' not in data:
            return "Invalid input", 400

        username = data['username']
        content = data['content']

        if len(username) == 0 or len(content) == 0:
            return "Username and content cannot be empty", 400

        with get_db() as conn:
            conn.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
            conn.commit()

        return jsonify({"message": "Message posted successfully"}), 200

@app.route('/')
def index():
    return '<h1>Welcome to MyForum</h1><p>Use the /messages endpoint to post and read messages.</p>'

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)