from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort = request.args.get('sort', default='DESC', type=str).upper()

        if sort not in ['ASC', 'DESC']:
            return jsonify({"error": "Invalid sort parameter"}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM messages ORDER BY id {sort} LIMIT ? OFFSET ?", (limit, offset))
        messages = cursor.fetchall()
        conn.close()

        return jsonify([dict(message) for message in messages]), 200

    elif request.method == 'POST':
        data = request.get_json()
        content = data.get('content')
        username = data.get('username')

        if not content or not username:
            return jsonify({"error": "Invalid input"}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (content, username) VALUES (?, ?)", (content, username))
        conn.commit()
        conn.close()

        return jsonify({"message": "Successful operation"}), 200

if __name__ == '__main__':
    # Create the database and the messages table if it doesn't exist
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000)