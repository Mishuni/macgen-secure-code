from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import html
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # Use an environment variable for the secret key
csrf = CSRFProtect(app)
DATABASE = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL
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

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.execute('SELECT username, content FROM messages ORDER BY id {} LIMIT ? OFFSET ?'.format(sort), (limit, offset))
            messages = cursor.fetchall()

        # Escape messages to prevent XSS
        escaped_messages = [(html.escape(username), html.escape(content)) for username, content in messages]
        return render_template('messages.html', messages=escaped_messages)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'content' not in data or 'username' not in data:
            return "Invalid input", 400

        username = data['username']
        content = data['content']

        # Validate username and content length
        if len(username) > 50 or len(content) > 500:
            return "Input too long", 400

        # Additional validation for content to prevent harmful input
        if any(char in content for char in ['<', '>', '&']):
            return "Invalid content", 400

        with sqlite3.connect(DATABASE) as conn:
            conn.execute('INSERT INTO messages (username, content) VALUES (?, ?)', (username, content))
            conn.commit()

        return "Message posted successfully", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)