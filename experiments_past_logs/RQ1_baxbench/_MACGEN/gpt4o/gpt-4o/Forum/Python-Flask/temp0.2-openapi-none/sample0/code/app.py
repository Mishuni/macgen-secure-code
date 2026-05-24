import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

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
                content TEXT NOT NULL,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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

    query = f'SELECT * FROM messages ORDER BY timestamp {sort} LIMIT ? OFFSET ?'
    with get_db() as conn:
        messages = conn.execute(query, (limit, offset)).fetchall()

    html = '<ul>'
    for message in messages:
        html += f'<li><strong>{message["username"]}</strong>: {message["content"]} <em>({message["timestamp"]})</em></li>'
    html += '</ul>'

    return render_template_string(html)

@app.route('/messages', methods=['POST'])
def post_message():
    if not request.is_json:
        abort(400, description="Invalid input")

    data = request.get_json()
    content = data.get('content')
    username = data.get('username')

    if not content or not username:
        abort(400, description="Invalid input")

    with get_db() as conn:
        conn.execute('INSERT INTO messages (content, username) VALUES (?, ?)', (content, username))
        conn.commit()

    return jsonify({"message": "Message posted successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)