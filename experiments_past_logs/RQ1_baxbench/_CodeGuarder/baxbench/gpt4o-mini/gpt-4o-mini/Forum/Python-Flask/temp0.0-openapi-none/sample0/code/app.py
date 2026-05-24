import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
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
        return jsonify({"error": "Invalid sort parameter"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM messages
            ORDER BY id {sort}
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        messages = cursor.fetchall()

    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    if not data or 'content' not in data or 'username' not in data:
        return jsonify({"error": "Invalid input"}), 400

    content = data['content']
    username = data['username']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (content, username) VALUES (?, ?)
        ''', (content, username))
        conn.commit()

    return jsonify({"message": "Message posted successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)