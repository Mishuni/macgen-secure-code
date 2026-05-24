import os
import sqlite3
from flask import Flask, request, jsonify, render_template, escape, abort

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET', 'default_secret_key')  # Ensure a consistent secret key

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')  # Use environment variable for database path

def init_db():
    with sqlite3.connect(DATABASE) as conn:
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

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        abort(500, description="Database connection failed")

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort = request.args.get('sort', default='DESC', type=str).upper()

        if sort not in ['ASC', 'DESC']:
            sort = 'DESC'

        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT username, content, timestamp FROM messages
            ORDER BY timestamp {} LIMIT ? OFFSET ?
        '''.format(sort)
        cursor.execute(query, (limit, offset))
        messages = cursor.fetchall()
        conn.close()

        # Escape user inputs before rendering
        messages_html = ''.join(
            f'<p><strong>{escape(username)}</strong>: {escape(content)} <em>{timestamp}</em></p>'
            for username, content, timestamp in messages
        )

        return render_template('messages.html', messages_html=messages_html)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'username' not in data or 'content' not in data:
            return jsonify({'error': 'Invalid input'}), 400

        username = data['username'].strip()
        content = data['content'].strip()

        if not username or not content:
            return jsonify({'error': 'Username and content cannot be empty'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (username, content) VALUES (?, ?)
        ''', (username, content))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Message posted successfully'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)